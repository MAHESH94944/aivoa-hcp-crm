from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """
    Manages application settings and environment variables.
    It automatically reads variables from the .env file.
    """
    DATABASE_URL: str
    GROQ_API_KEY: str

    class Config:
        # This tells pydantic-settings where to find your variables
        env_file = ".env"

# Create a single, reusable instance of the settings
settings = Settings()