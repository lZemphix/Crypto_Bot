from pybit.unified_trading import WebSocket
from pybit.unified_trading import HTTP
from client.klines import Klines
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
    def format_balance(balance: dict):
        formated_balance = {}
        coins = balance["result"]["list"][0]["coin"]
        for n in range(len(coins)):
            formated_balance[coins[n].get("coin")] = float(
                coins[n].get("walletBalance")
            )
        return formated_balance


class GatekeeperStorage:

    def __init__(self, klines: Klines, client: HTTP, account_type: str):
        self.klines = klines
        self.client = client
        self.account_type = account_type
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

    def __req_update(self, target: str):
        try:
            if target.lower() == "klines":
                updating_value = self.klines.get_klines()[::-1]

            elif target.lower() == "balance":
                balance = self.client.get_wallet_balance(accountType=self.account_type)
                updating_value = Formater().format_balance(balance)
            else:
                raise ValueError('Expecting "klines" or "balance" in the target value')
            self.update(target, updating_value)
        except Exception as e:
            logger.exception(f"_req_update error: {e}")

    def update_balance(self):
        try:
            self.__req_update("balance")
            logger.debug("Balance part in the journal was updated")
            return True
        except Exception as e:
            logger.error(e)

    def update_klines(self):
        try:
            self.__req_update("klines")
            logger.debug("Klines part in the journal was updated")
            return True
        except Exception as e:
            logger.error(e)


class Gatekeeper:

    def __init__(self, gatekeeper_storage: GatekeeperStorage, symbol: str, interval: int):
        self.gatekeeper_storage = gatekeeper_storage
        self.symbol = symbol
        self.interval = interval
        self.ws = WebSocket(channel_type="spot", testnet=False)
        self.ws.kline_stream(
            interval=self.interval, symbol=self.symbol, callback=self.klines_callback
        )

    def klines_callback(self, kline: dict):
        storage = self.gatekeeper_storage.get()
        new_kline = list(Formater().format_new_kline(kline).values())

        if len(storage["klines"]) == 0 or new_kline[-1] == True:
            self.gatekeeper_storage.update_klines()
            return
        if len(storage["balance"]) == 0:
            self.gatekeeper_storage.update_balance()
            return

        klines_list = storage["klines"]
        klines_list.pop()
        klines_list.append(new_kline[:-1])
        self.gatekeeper_storage.update("klines", klines_list)
        logger.debug("Last kline was updated")
