from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sshtunnel import SSHTunnelForwarder

from app.config import settings

_tunnel: SSHTunnelForwarder | None = None
_engine: Engine | None = None


class Base(DeclarativeBase):
    pass


def _start_tunnel() -> SSHTunnelForwarder:
    tunnel = SSHTunnelForwarder(
        (settings.SSH_HOST, settings.SSH_PORT),
        ssh_username=settings.SSH_USER,
        ssh_password=settings.SSH_PASSWORD,
        remote_bind_address=("127.0.0.1", settings.DB_PORT),
    )
    tunnel.start()
    return tunnel


def get_database_url(host: str, port: int) -> str:
    return (
        f"postgresql://{quote_plus(settings.DB_USER)}:{quote_plus(settings.DB_PASSWORD)}"
        f"@{host}:{port}/{settings.DB_NAME}"
    )


def get_engine() -> Engine:
    global _engine
    if _engine is not None:
        return _engine

    global _tunnel
    _tunnel = _start_tunnel()
    _engine = create_engine(
        get_database_url("127.0.0.1", _tunnel.local_bind_port),
        pool_pre_ping=True,
        pool_recycle=300,
    )
    SessionLocal.configure(bind=_engine)
    return _engine


SessionLocal = sessionmaker(autocommit=False, autoflush=False)


def get_db():
    get_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
