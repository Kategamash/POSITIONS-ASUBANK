from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # БД доступна только через SSH-туннель
    DB_HOST: str = "85.208.86.39"
    DB_PORT: int = 5432
    DB_NAME: str = "asu_bank_db"
    DB_USER: str = "asu_bank_group_user"
    DB_PASSWORD: str = "qzwxecasd@501105"

    SSH_HOST: str = "85.208.86.39"
    SSH_PORT: int = 22
    SSH_USER: str = "guest_for_db"
    SSH_PASSWORD: str = "guest_db_123"

    SECRET_KEY: str = "positions-asubank-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    class Config:
        env_file = ".env"


settings = Settings()
