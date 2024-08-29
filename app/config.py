from pydantic import (
    AmqpDsn,
    Field,
    PostgresDsn,
    SecretStr
)
from pydantic_settings import BaseSettings
from dotenv import load_dotenv, find_dotenv
import logging
from logging.handlers import RotatingFileHandler

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

class Logger:
    @classmethod
    def get_logger(cls, name: str = __name__, log_file: str = "app.log", level: int = logging.INFO) -> logging.Logger:
        # Create a logger
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Create handlers
        console_handler = logging.StreamHandler()
        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)  # 5 MB per file

        # Create formatters and add it to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to the logger
        if not logger.handlers:  # Avoid adding handlers multiple times
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

        return logger

# Example usage
logger = Logger.get_logger()
logger.info("This is an info message.")
                                                                                                                                              

settings= Settings()
    
