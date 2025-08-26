from logging import getLogger
import time
from client.base import BotBase
from client.orders import Orders
from utils.gatekeeper import gatekeeper_storage
from utils.journal_manager import JournalManager
from utils.triggers import CrossKlinesTrigger

logger = getLogger(__name__)


class Checkup(BotBase):

    def __init__(self) -> None:
        super().__init__()
        self.orders = Orders()

    def price_valid(self):
        actual_price = float(gatekeeper_storage.get_klines()[-2][4])
        sell_price = self.orders.get_avg_order() + self.stepSell
        return actual_price >= sell_price


class Notifier(Checkup):

    def __init__(self):
        super().__init__()

    def send_buy_notify(self):
        last_order = self.orders.get_order_history()[0]
        last_order_price = float(last_order["avgPrice"])
        coin_qty = float(last_order["cumExecQty"])
        self.telenotify.sold(
            f"Bot was sold```\n{coin_qty:.10f} {self.coin_name} for {last_order_price}.\nTotal: price: {coin_qty*last_order_price}```"
        )


class Sell(Checkup):

    def __init__(self) -> None:
        super().__init__()
        self.journal = JournalManager()
        self.trigger = CrossKlinesTrigger()

    def activate(self) -> bool:
        logger.info("Trying to close positions")
        if self.price_valid():
            logger.debug("Price valid for sell")
            if self.trigger.cross_up_to_down():
                logger.debug("Trigger cross_up_to_down activated")
                gatekeeper_storage.update_balance()
                if self.orders.place_sell_order():
                    logger.info("Sell order placed successfully")
                    time.sleep(2)
                    Notifier().send_buy_notify()
                    logger.info("Notification sent for sell")
                    self.journal.clear()
                    logger.info("Journal cleared after sell")
                    return True
