from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "DK Invoice Calendar"
    SECRET_KEY: str = "supersecretkey-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/dk_invoices"
    
    SUPERADMIN_EMAIL: str = "super@example.com"
    SUPERADMIN_PASSWORD: str = "super123"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
