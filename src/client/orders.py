from logging import getLogger
from client.base import Client
from client.account import account
from config.config import get_bot_config
from utils.exceptions import (
    IncorrectOpenOrdersList,
    IncorrectOrdersHistory,
    OrderPlaceExeption,
)


logger = getLogger(__name__)


class Orders(Client):
    def __init__(self):
        super().__init__()

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
                qty=get_bot_config("amountBuy"),
            )
            return True
        except Exception as e:
            logger.error(e)
            return False

    def place_sell_order(self) -> bool:
        """Places sell order"""
        try:
            coin_name = self.symbol.replace("USDT", "")
            amount = str(account.get_balance().get(coin_name))[:8]
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
            raise OrderPlaceExeption(f"Message: {e}")


get_orders = Orders()
