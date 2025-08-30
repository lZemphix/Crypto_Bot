from logging import getLogger
import time
from client.orders import Orders
from src.utils.telenotify import Telenotify
from utils.gatekeeper import GatekeeperStorage
from utils.journal_manager import JournalManager
from utils.metadata_manager import MetaManager
from utils.triggers import CrossKlinesTrigger

logger = getLogger(__name__)


class Checkup:

    def __init__(
        self, gatekeeper_storage: GatekeeperStorage, orders: Orders, step_sell: float
    ) -> None:
        self.gatekeeper_storage = gatekeeper_storage
        self.orders = orders
        self.step_sell = step_sell

    def price_valid(self):
        actual_price = float(self.gatekeeper_storage.get_klines()[-2][4])
        sell_price = self.orders.get_avg_order() + self.step_sell
        return actual_price >= sell_price


class Notifier:

    def __init__(
        self,
        telenotify: Telenotify,
        coin_name: str,
        gatekeeper_storage: GatekeeperStorage,
        journal: JournalManager,
        orders: Orders,
    ) -> None:
        self.telenotify = telenotify
        self.gatekeeper_storage = gatekeeper_storage
        self.journal = journal
        self.coin_name = coin_name
        self.orders = orders

    def send_buy_notify(self):
        last_order = self.orders.get_order_history()[0]
        last_order_price = float(last_order["avgPrice"])
        coin_qty = float(last_order["cumExecQty"])
        self.telenotify.sold(
            f"Bot was sold```\n{coin_qty:.10f} {self.coin_name} for {last_order_price}.\nTotal: price: {coin_qty*last_order_price}```"
        )


class Sell:

    def __init__(
        self,
        journal: JournalManager,
        trigger: CrossKlinesTrigger,
        checkup: Checkup,
        gatekeeper_storage: GatekeeperStorage,
        orders: Orders,
        notifier: Notifier,
        metamanager: MetaManager,
    ) -> None:
        self.journal = journal
        self.trigger = trigger
        self.checkup = checkup
        self.gatekeeper_storage = gatekeeper_storage
        self.orders = orders
        self.notifier = notifier
        self.metamanager = metamanager

    def activate(self) -> bool:
        if self.checkup.price_valid():
            logger.debug("Price valid for sell")
            if self.trigger.cross_up_to_down():
                logger.debug("Trigger cross_up_to_down activated")
                if self.gatekeeper_storage.update_balance():
                    if self.orders.place_sell_order():
                        logger.info("Sell order placed successfully")
                        time.sleep(2)
                        self.notifier.send_buy_notify()
                        logger.info("Notification sent for sell")
                        self.metamanager.update_all(type="sell")
                        self.journal.clear()
                        logger.info("Journal cleared after sell")
                        return True
