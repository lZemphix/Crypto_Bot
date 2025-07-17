from logging import getLogger
import time
from client.base import BotBase
from client.klines import Klines
from client.orders import Orders
from utils.gatekeeper import gatekeeper
from utils.journal_manager import JournalManager
from utils.states import SellState
from utils.telenotify import Telenotify
from utils.triggers import CrossKlinesTrigger

logger = getLogger(__name__)


class Sell(BotBase):

    def __init__(self) -> None:
        super().__init__()
        self.klines = Klines()
        self.journal = JournalManager()
        self.orders = Orders()
        self.trigger = CrossKlinesTrigger()
        self.telenotify = Telenotify()
        self.current_state = SellState.WAITING
        self.transisions = SellState.transitions()

    def get_avg_order(self):
        orders = self.journal.get()["orders"]
        return (sum(orders) / len(orders)) if len(orders) > 0 else 0

    def price_valid(self):
        actual_price = gatekeeper.get_updated_klines()
        sell_price = self.get_avg_order() + self.stepSell
        try:
            if actual_price != None:
                if isinstance(actual_price, list):
                    actual_price = float(actual_price[0][4])
            else:
                actual_price = 0
        except:
            pass
        logger.debug(actual_price)
        return actual_price >= sell_price

    def _send_notify(self):
        last_order = self.orders.get_order_history()[0]
        last_order_price = float(last_order["avgPrice"])
        coin_qty = float(last_order["cumExecQty"])
        self.telenotify.sold(
            f"Bot was sold {coin_qty} {self.coin_name} for {last_order_price}.\nTotal: price: {coin_qty*last_order_price}"
        )

    def activate(self) -> bool:
        if self.price_valid():
            logger.info("price valid")
            if self.trigger.cross_up_to_down():
                logger.info("cross")
                if self.orders.place_sell_order():
                    time.sleep(2)
                    self._send_notify()
                    self.journal.clear()
                    return True
