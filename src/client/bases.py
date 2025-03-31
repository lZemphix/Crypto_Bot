from config.config import get_bot_config, get_env_config
from utils.states import BuyState
from utils.telenotify import TeleNotify
from pybit.unified_trading import HTTP
from logging import getLogger
import json

logger = getLogger(__name__)

class Client:

    def __init__(self) -> None:      
        self.API_KEY = get_env_config("API_KEY")
        self.API_KEY_SECRET = get_env_config("API_KEY_SECRET")
        self.ACCOUNT_TYPE = get_env_config("ACCOUNT_TYPE")
        self.symbol = get_bot_config('symbol')
        self.amount_buy = get_bot_config('amountBuy')
        self.interval = get_bot_config('interval')
        self.client = HTTP(testnet=False, 
                           api_key=self.API_KEY, 
                           api_secret=self.API_KEY_SECRET, 
                           logging_level=30)
        

class BotBase:
    def __init__(self) -> None:

        self.symbol: str = get_bot_config('symbol')
        self.coin_name: str = self.symbol.replace('USDT', '')
        self.interval: str = get_bot_config('interval')
        self.amount_buy: float = get_bot_config('amountBuy')
        self.stepBuy: float = get_bot_config('stepBuy')
        self.stepSell: float = get_bot_config('stepSell')
        self.send_notify: bool = get_bot_config('send_notify')
        self.RSI: float = get_bot_config('RSI')
        
        self.notify = TeleNotify(True if self.send_notify else False)

        self.current_state = ''
        self.transitions = {}

    def change_state(self, new_state: BuyState) -> bool:
        if new_state in self.transitions[self.current_state]:
            logger.debug('Changing state from %s to %s', self.current_state, new_state)
            self.current_state = new_state
            return True
        
    def get_current_state(self):
        return self.current_state
    