from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database Settings
    DATABASE_URL: str
    
    # AI Providers
    GEMINI_API_KEY: str

    # Pydantic will automatically look for a .env file to populate these values
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Create a global instance of settings to use throughout the app
settings = Settings()