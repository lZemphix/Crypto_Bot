import sys
import time
from client.account import account
from client.klines import get_klines
from logging import getLogger

logger = getLogger(__name__)


class Gatekeeper:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.valid_data = {"balance": {}, "klines": []}
        return cls._instance

    def get(self) -> dict:
        return self.valid_data

    def update_balance(self) -> bool:
        try:
            balance = account.get_balance()
        except Exception:
            balance = self.get()["balance"]
            logger.info("except balance")
        self.valid_data["balance"] = balance
        return True

    def update_klines(self) -> bool:
        try:
            klines = get_klines.get_klines()
            time.sleep(0.5)
        except Exception:
            klines = self.get()["klines"]
            logger.info("except klines")
        self.valid_data["klines"] = klines
        return True

    def get_updated_balance(self):
        try:
            self.update_balance()
        except Exception:
            pass
        return self.get()["balance"]

    def get_updated_klines(self):
        try:
            self.update_klines()
        except Exception:
            pass
        return self.get()["klines"]

gatekeeper = Gatekeeper()
