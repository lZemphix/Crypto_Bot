from logging import getLogger
import time
from client.base import BotBase
from client.orders import Orders
from utils.gatekeeper import gatekeeper
from utils.journal_manager import JournalManager
from utils.states import SellState
from utils.telenotify import Telenotify
from utils.triggers import CrossKlinesTrigger

logger = getLogger(__name__)


class Checkup(BotBase):

    def __init__(self) -> None:
        super().__init__()
        self.orders = Orders()
        self.telenotify = Telenotify()

    def price_valid(self):
        actual_price = gatekeeper.get_updated_klines()
        sell_price = self.orders.get_avg_order() + self.stepSell
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

    def send_notify(self):
        last_order = self.orders.get_order_history()[0]
        last_order_price = float(last_order["avgPrice"])
        coin_qty = float(last_order["cumExecQty"])
        self.telenotify.sold(
            f"Bot was sold {coin_qty} {self.coin_name} for {last_order_price}.\nTotal: price: {coin_qty*last_order_price}"
        )


class Sell(Checkup):

    def __init__(self) -> None:
        super().__init__()
        self.journal = JournalManager()
        self.trigger = CrossKlinesTrigger()
        self.current_state = SellState.WAITING

    def activate(self) -> bool:
        logger.info("Sell activation started")
        if self.price_valid():
            logger.info("Price valid for sell")
            if self.trigger.cross_up_to_down():
                logger.info("Trigger cross_up_to_down activated")
                if self.orders.place_sell_order():
                    logger.info("Sell order placed successfully")
                    time.sleep(2)
                    self.send_notify()
                    logger.info("Notification sent for sell")
                    self.journal.clear()
                    logger.info("Journal cleared after sell")
                    return True
