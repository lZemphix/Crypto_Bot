from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    DB_NAME: str = os.getenv("DB_NAME")

    @property
    def db_url(self) -> str:
        return f"sqlite:///{self.DB_NAME}.sqlite"


settings = Settings()
