import json
import time
from pybit.unified_trading import WebSocket, HTTP
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
    



class GatekeeperInterface:

    def __init__(self):
        super().__init__()
        self.path = "src/data/gatekeeper_journal.json"

    def get(self) -> dict[dict[float], dict[float]]:
        with open(self.path) as f:
            return json.load(f)

    def get_balance(self) -> dict[float]:
        return self.get()["balance"]

    def get_klines(self) -> dict[float]:
        return self.get()["klines"]


class GatekeeperWebsocket(GatekeeperInterface, Client):

    def __init__(self):
        super().__init__()
        self.path = "src/data/gatekeeper_journal.json"
        self.ws = WebSocket(channel_type="spot", testnet=False)
        self.wallet_ws = WebSocket(
            channel_type="private",
            testnet=False,
            api_key=self.API_KEY,
            api_secret=self.API_KEY_SECRET,
        )
        self.ws.kline_stream(
            interval=5, symbol="BTCUSDT", callback=self.klines_callback
        )
        self.wallet_ws.wallet_stream(callback=self.wallet_callback)
        

    def get(self):
        with open(self.path) as f:
            return json.load(f)

    def get_balance(self):
        return self.get()["balance"]

    def get_klines(self):
        return self.get()["klines"]
    
    def __update(self, target: str):
        try:
            journal = self.get()

            if target.lower() == 'klines':
                updating_value = get_klines.get_klines()[::-1] 

            elif target.lower() == 'balance':
                updating_value = Formater().format_balance(self.client.get_wallet_balance(accountType=self.ACCOUNT_TYPE), 'init')
            else:
                raise ValueError('Expecting "klines" or "balance" in the target value')
            journal[target] = updating_value
            with open(self.path, 'w') as f:
                json.dump(journal, f, indent=4)
        except Exception as e:
            logger.error(e)

    
    def update_balance_journal(self):
        try:
            self.__update('balance')
            logger.debug("Balance part in the journal was updated")
        except Exception as e:
            logger.error(e)


    def update_klines_journal(self):
        try:
            self.__update('klines')
            logger.debug("Klines part in the journal was updated")
        except Exception as e:
            logger.error(e)


    def klines_callback(self, kline: dict):
        journal = self.get()
        new_kline = list(Formater().format_new_kline(kline).values())

        if len(journal['klines']) == 0 or new_kline[-1] == True:
            self.update_klines_journal()
            return
        if len(journal['balance']) == 0:
            self.update_balance_journal()
            return
        
        journal["klines"].pop()
        journal["klines"].append(new_kline[:-1])
        with open(self.path, "w") as f:
            json.dump(journal, f, indent=4)
            logger.debug("Last kline was updated")

    def wallet_callback(self, balance):
        journal = self.get()
        formated_balance = Formater().format_balance(balance)
        journal["balance"] = formated_balance
        with open(self.path, "w") as f:
            json.dump(journal, f, indent=4)
        logger.debug("Wallet change detected! Updating journal!")


gatekeeper = GatekeeperInterface()
gatekeeper_websocket = GatekeeperWebsocket()
