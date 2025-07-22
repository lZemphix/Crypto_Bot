import json
import time
from pybit.unified_trading import WebSocket
from client.base import Client
from client.klines import get_klines
from logging import getLogger

logger = getLogger(__name__)


class Formater:

    def __init__(self):
        pass

    @staticmethod
    def format_new_kline(kline) -> dict:
        new_order = ["timestamp", "open", "high", "low", "close", "turnover", "confirm"]
        new_kline: dict = kline["data"][0]
        formated_kline = {k: new_kline[k] for k in new_order}
        return formated_kline

    @staticmethod
    def format_balance(balance: dict, method: str = 'websocket'):
        formated_balance = {}
        if method == 'websocket':
            coins = balance["data"][0]["coin"]
        elif method == 'init':
            coins = balance['result']['list'][0]['coin']
        else:
            raise ValueError('Method can be only "websocket" or "init"')
        for n in range(len(coins)):
            formated_balance[coins[n].get("coin")] = float(
                coins[n].get("walletBalance")
            )
        return formated_balance
    



class GatekeeperStorage(Client):

    def __init__(self):
        super().__init__()
        self.storage: dict = {"balance": {}, "klines": []}

    def get(self) -> dict[dict[float], dict[float]]:
        return self.storage

    def get_balance(self) -> dict[float]:
        return self.storage.get("balance")

    def get_klines(self) -> dict[float]:
        return self.storage.get("klines")
    
    def update(self, target: str, data: list | dict):
        try:
            self.storage[target] = data
            return True
        except Exception as e:
            logger.error(e)
    
    def __init_update(self, target: str):
        try:
            if target.lower() == 'klines':
                updating_value = get_klines.get_klines()[::-1] 

            elif target.lower() == 'balance':
                balance = self.client.get_wallet_balance(accountType=self.ACCOUNT_TYPE)
                updating_value = Formater().format_balance(balance, 'init')
            else:
                raise ValueError('Expecting "klines" or "balance" in the target value')
            self.update(target, updating_value)
        except Exception as e:
            logger.error(e)

    
    def update_balance(self):
        try:
            self.__init_update('balance')
            logger.debug("Balance part in the journal was updated")
            return True
        except Exception as e:
            logger.error(e)


    def update_klines(self):
        try:
            self.__init_update('klines')
            logger.debug("Klines part in the journal was updated")
            return True
        except Exception as e:
            logger.error(e)



gatekeeper_storage = GatekeeperStorage()

class Gatekeeper(Client):

    def __init__(self):
        super().__init__()
        self.ws = WebSocket(
            channel_type="spot", 
            testnet=False
        )
        self.wallet_ws = WebSocket(
            channel_type="private",
            testnet=False,
            api_key=self.API_KEY,
            api_secret=self.API_KEY_SECRET,
        )
        self.ws.kline_stream(
            interval=5, symbol="BTCUSDT", callback=self.klines_callback
        )
        self.wallet_ws.wallet_stream(
            callback=self.wallet_callback
        )


    def klines_callback(self, kline: dict):
        storage = gatekeeper_storage.get()
        new_kline = list(Formater().format_new_kline(kline).values())

        if len(storage['klines']) == 0 or new_kline[-1] == True:
            gatekeeper_storage.update_klines()
            return
        if len(storage['balance']) == 0:
            gatekeeper_storage.update_balance()
            return
        
        klines_list = storage["klines"]
        klines_list.pop()
        klines_list.append(new_kline[:-1])
        gatekeeper_storage.update('klines', klines_list)
        logger.debug("Last kline was updated")
            

    def wallet_callback(self, balance):
        formated_balance = Formater().format_balance(balance)
        gatekeeper_storage.update(balance, formated_balance)
        logger.debug("Wallet change detected! Updating journal!")
