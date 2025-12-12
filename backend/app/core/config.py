from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "DK Invoice Calendar API"
    SECRET_KEY: str = "supersecretkey-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    DATABASE_URL: str = "sqlite:///./dev.db"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    SUPERADMIN_EMAIL: str = "super@example.com"
    SUPERADMIN_PASSWORD: str = "super123"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
