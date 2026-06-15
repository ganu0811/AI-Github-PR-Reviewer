from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    github_webook_secret: str = ""
    
    class Config:
        env_file: ".env"
        