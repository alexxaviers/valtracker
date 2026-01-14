from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    grid_api_key: str
    grid_file_api_base_url: str = "https://api.grid.gg/file-download"
    cache_dir: str = "./data/cache"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
