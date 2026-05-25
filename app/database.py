from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sshtunnel import SSHTunnelForwarder

from app.config import settings

_tunnel: SSHTunnelForwarder | None = None


def _start_tunnel() -> SSHTunnelForwarder:
    tunnel = SSHTunnelForwarder(
        (settings.SSH_HOST, settings.SSH_PORT),
        ssh_username=settings.SSH_USER,
        ssh_password=settings.SSH_PASSWORD,
        remote_bind_address=("127.0.0.1", settings.DB_PORT),
    )
    tunnel.start()
    return tunnel


def _make_engine():
    global _tunnel
    _tunnel = _start_tunnel()
    local_port = _tunnel.local_bind_port
    from urllib.parse import quote_plus
    url = (
        f"postgresql://{quote_plus(settings.DB_USER)}:{quote_plus(settings.DB_PASSWORD)}"
        f"@127.0.0.1:{local_port}/{settings.DB_NAME}"
    )
    return create_engine(url, pool_pre_ping=True, pool_recycle=300)


engine = _make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
