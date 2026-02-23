from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Using SQLite as fallback since Docker/PostgreSQL isn't natively installed on this system
    database_url: str = "sqlite:///./drought_db.sqlite"
    
    class Config:
        env_file = ".env"

settings = Settings()
