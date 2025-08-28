import json
from logging import getLogger
from utils.gatekeeper import GatekeeperStorage
from config.config import get_bot_config
from utils.exceptions import (
    IncorrectOpenOrdersList,
    IncorrectOrdersHistory,
    OrderPlaceException,
)
from utils.journal_manager import JournalManager
from pybit.unified_trading import HTTP


logger = getLogger(__name__)


class Checkup:
    def __init__(self, client: HTTP, symbol: str):
        self.client = client
        self.symbol = symbol

    def get_accuracy(self) -> int:
        info = self.client.get_instruments_info(category="spot", symbol=self.symbol)
        min_order_qty = info["result"]["list"][0]["lotSizeFilter"]["minOrderQty"]
        return len(min_order_qty)


class Orders(Checkup):
    def __init__(self, client: HTTP, symbol: str, journal: JournalManager, gatekeeper_storage: GatekeeperStorage, amount_buy: float):
        super().__init__(client=client, symbol=symbol)
        self.journal = journal
        self.gatekeeper_storage = gatekeeper_storage
        self.amount_buy = amount_buy

    def get_order_history(self) -> dict:
        """cancelType: [CancelByUser | UNKNOWN]
        cumExecValue: [float] - in usdt
        cumExecQty [float] - in second coin"""
        try:
            history = self.client.get_order_history(category="spot")["result"]["list"]
            return history
        except Exception as e:
            raise IncorrectOrdersHistory(
                f"Incorrect data received from exchange. Message: {e}"
            )

    def get_open_orders(self) -> list:
        """Return open orders list"""
        try:
            open_orders = self.client.get_open_orders(category="spot")["result"]["list"]
            return open_orders
        except Exception as e:
            raise IncorrectOpenOrdersList(
                f"Incorrect data received from exchange. Message: {e}"
            )

    def place_buy_order(self) -> bool:
        """Place buy order"""
        try:
            self.client.place_order(
                category="spot",
                symbol=self.symbol,
                side="Buy",
                orderType="Market",
                marketUnit="quoteCoin",
                qty=self.amount_buy,
            )
            return True
        except Exception as e:
            logger.error(e)
            return False

    def place_sell_order(self) -> bool:
        """Places sell order"""
        try:
            coin_name = self.symbol.replace("USDT", "")
            amount = f"{self.gatekeeper_storage.get_balance().get(coin_name):.10f}"[
                : self.get_accuracy()
            ]
            logger.info(f"{amount=}")
            self.client.place_order(
                category="spot",
                symbol=self.symbol,
                side="Sell",
                orderType="Market",
                qty=amount,
            )
            return True
        except Exception as e:
            logger.error(e)
            raise OrderPlaceException(f"Message: {e}")

    def get_avg_order(self) -> float:
        orders = self.journal.get()["orders"]
        return (sum(orders) / len(orders)) if len(orders) > 0 else 0
