from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):

    @property
    def db_url(self) -> str:
        return f"sqlite:///statistic.sqlite"


settings = Settings()
