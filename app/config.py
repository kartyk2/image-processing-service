from pydantic import (
    AmqpDsn,
    Field,
    PostgresDsn,
    SecretStr
)
from pydantic_settings import BaseSettings
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Settings(BaseSettings):
    api_key: SecretStr = Field(..., env='API_KEY')  
    database_url: PostgresDsn = Field(..., env='DATABASE_URL')
    rabbitmq_host: str = Field(..., env='RABBITMQ_HOST')
    rabbitmq_port: int = Field(..., env='RABBITMQ_PORT')
    rabbitmq_user: str = Field(..., env='RABBITMQ_USER')
    rabbitmq_password: str = Field(..., env='RABBITMQ_PASSWORD')
    secret_key: str = Field(..., env='SECRET_KEY')

    @property
    def amqp_dsn(self) -> AmqpDsn:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}/"


    secret_key: SecretStr = Field(..., env='SECRET_KEY')
    debug: bool = Field(False, env='DEBUG')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra= 'allow'

settings = Settings()
