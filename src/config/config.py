from pydantic_settings import BaseSettings, SettingsConfigDict
import json
from logging import getLogger
from pybit.unified_trading import HTTP
logger = getLogger(__name__)


def get_bot_config(param: str = None):
    try:
        with open("bot_config.json", "r") as f:
            config: dict = json.load(f)
            if param == None:
                return config
            return config.get(param)
    except Exception as e:
        logger.error(e)


class BotSettings(BaseSettings):
    symbol: str = get_bot_config("symbol")
    interval: int = get_bot_config("interval")
    amountBuy: float = get_bot_config("amountBuy")
    RSI: int = get_bot_config("RSI")
    stepBuy: float = get_bot_config("stepBuy")
    stepSell: float = get_bot_config("stepSell")
    send_notify: bool = get_bot_config("send_notify")

class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
 
    ACCOUNT_TYPE: str
    API_KEY_SECRET: str
    API_KEY: str
    BOT_TOKEN: str
    CHAT_ID: str
    USERNAME: str
    PASSWORD: str

    @property
    def get_client(self):
        return HTTP(
            testnet=False,
            api_key=self.API_KEY,
            api_secret=self.API_KEY_SECRET,
            logging_level=30,
        )

bot_settings = BotSettings()
env_settings = EnvSettings()