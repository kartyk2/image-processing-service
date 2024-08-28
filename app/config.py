from pydantic import (
    AmqpDsn,
    Field,
    PostgresDsn,
    SecretStr
)
from pydantic_settings import BaseSettings
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())

class Settings(BaseSettings):
    api_key: SecretStr = Field(..., env='API_KEY')  
    pg_dsn: PostgresDsn = Field(..., env='DATABASE_URL')
    amqp_dsn: AmqpDsn = Field(..., env='AMQP_DSN')

    secret_key: SecretStr = Field(..., env='SECRET_KEY')
    debug: bool = Field(False, env='DEBUG')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

@lru_cache
settings = Settings()
