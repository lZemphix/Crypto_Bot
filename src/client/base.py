from config.config import get_bot_config, get_env_config
from utils.states import BuyState
from utils.telenotify import TeleNotify
from pybit.unified_trading import HTTP
from logging import getLogger

logger = getLogger(__name__)


class Client:

    def __init__(self) -> None:
        self.API_KEY = get_env_config("API_KEY")
        self.API_KEY_SECRET = get_env_config("API_KEY_SECRET")
        self.ACCOUNT_TYPE = get_env_config("ACCOUNT_TYPE")
        self.symbol = get_bot_config("symbol")
        self.amount_buy = get_bot_config("amountBuy")
        self.interval = get_bot_config("interval")
        self.client = HTTP(
            testnet=False,
            api_key=self.API_KEY,
            api_secret=self.API_KEY_SECRET,
            logging_level=30,
        )


class Bot:
    def __init__(self) -> None:

        self.symbol: str = get_bot_config("symbol")
        self.coin_name: str = self.symbol.replace("USDT", "")
        self.interval: str = get_bot_config("interval")
        self.amount_buy: float = get_bot_config("amountBuy")
        self.stepBuy: float = get_bot_config("stepBuy")
        self.stepSell: float = get_bot_config("stepSell")
        self.send_notify: bool = get_bot_config("send_notify")
        self.RSI: float = get_bot_config("RSI")
        self.notify = TeleNotify(True if self.send_notify else False)
