import time
from client.orders import Orders
from logging import getLogger

from src.utils.telenotify import Telenotify
from utils.gatekeeper import GatekeeperStorage
from utils.journal_manager import JournalManager
from utils.lines_manager import LinesManager
from utils.metadata_manager import MetaManager
from utils.states import BuyState
from utils.triggers import CrossKlinesTrigger

logger = getLogger(__name__)


class Checkup:

    def __init__(
        self,
        trigger: CrossKlinesTrigger,
        gatekeeper_storage: GatekeeperStorage,
        orders: Orders,
        journal: JournalManager,
        amount_buy: float,
        step_buy: float
    ) -> None:
        self.trigger = trigger
        self.gatekeeper_storage = gatekeeper_storage
        self.orders = orders
        self.journal = journal
        self.amount_buy = amount_buy
        self.step_buy = step_buy

    def valid_balance(self):
        usdt_balance = self.gatekeeper_storage.get_balance()["USDT"]
        return usdt_balance > self.amount_buy

    def valid_price(self):
        avg_order = self.orders.get_avg_order()
        actual_price = float(self.gatekeeper_storage.get_klines()[-2][4])
        price_lower_than_step = self.step_buy < (avg_order - actual_price)
        return actual_price < avg_order and price_lower_than_step

    def update_journal(self, last_order: float):
        data = self.journal.get()
        orders = data["orders"]
        orders.append(last_order)
        data["orders"] = orders
        self.journal.update(data)
        return True


class Notifier:
    def __init__(
        self,
        telenotify: Telenotify,
        gatekeeper_storage: GatekeeperStorage,
        journal: JournalManager,
        ) -> None: 
        self.telenotify = telenotify
        self.gatekeeper_storage = gatekeeper_storage
        self.journal = journal

    def send_averaging_notify(self, last_order: float):
        self.gatekeeper_storage.update_balance()
        balance = self.gatekeeper_storage.get_balance()
        min_sell_price = self.journal.get()["sell_lines"][0]
        min_buy_price = self.journal.get()["buy_lines"][0]
        logger.info(
            f'Avergaging for ${last_order}. Balance: {balance["USDT"]}. Min price for sell: ${min_sell_price}. Min price for averate: ${min_buy_price}'
        )
        self.telenotify.bought(
            f'```\nAverage price: {last_order} USDT\nBalance: {balance["USDT"]}\nSell line: ${min_sell_price}\nAverage line: ${min_buy_price}```'
        )


class Averaging:

    def __init__(
        self,
        lines: LinesManager,
        checkup: Checkup,
        trigger: CrossKlinesTrigger,
        gatekeeper_storage: GatekeeperStorage,
        orders: Orders,
        metamanager: MetaManager,
        notifier: Notifier
    ) -> None:
        self.current_state = BuyState.WAITING
        self.lines = lines
        self.checkup = checkup
        self.trigger = trigger
        self.gatekeeper_storage = gatekeeper_storage
        self.orders = orders
        self.metamanager = metamanager
        self.notifier = notifier

    def activate(self):
        logger.info("Trying to average")
        if self.checkup.valid_balance():
            logger.debug("valid_balance")
            if self.checkup.valid_price():
                logger.debug("valid_price")
                if self.trigger.cross_down_to_up():
                    logger.debug("Trigger cross_down_to_up activated")
                    self.gatekeeper_storage.update_balance()
                    if self.orders.place_buy_order():
                        logger.info("Buy order placed successfully")
                        time.sleep(2)
                        last_order = self.orders.get_order_history()[0].get("avgPrice")
                        logger.debug(f"Last order price: {last_order}")
                        if self.checkup.update_journal(float(last_order)):
                            logger.debug("Journal updated with new order")
                            if self.lines.write_lines(float(last_order)):
                                logger.debug("Lines written successfully")
                                self.metamanager.update_all(type="average")
                                logger.debug("Metadata was writed")
                                self.notifier.send_averaging_notify(last_order)
                                return True
