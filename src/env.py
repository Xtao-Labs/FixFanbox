from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class EnvConfig(BaseSettings):
    DEBUG: bool = True
    LISTEN: str = "0.0.0.0"
    PORT: int = 8080


env_config = EnvConfig()
