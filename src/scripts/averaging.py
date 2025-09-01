import time
from typing import List
from client.orders import Orders
from logging import getLogger

from utils.telenotify import Telenotify
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
        gatekeeper_storage: GatekeeperStorage,
        orders: Orders,
        journal: JournalManager,
        amount_buy: float,
        step_buy: float,
    ) -> None:
        self.gatekeeper_storage = gatekeeper_storage
        self.orders = orders
        self.journal = journal
        self.amount_buy = amount_buy
        self.step_buy = step_buy

    def valid_balance(self) -> bool:
        try:
            usdt_balance = self.gatekeeper_storage.get_balance()["USDT"]
            return usdt_balance > self.amount_buy
        except TypeError as e:
            logger.exception(f"TypeError! Message: {e}")

    def valid_price(self) -> bool:
        """Checking condition: actial price must be higher than avg order and lower is one step"""
        try:
            avg_order = self.orders.get_avg_order()
            actual_price = float(self.gatekeeper_storage.get_klines()[-1][4])
            price_lower_than_step = self.step_buy < (avg_order - actual_price)
            return actual_price < avg_order and price_lower_than_step
        except TypeError as e:
            logger.exception(f"TypeError! Message: {e}")
        except IndexError as e:
            logger.exception(f"IndexError! Message: {e}")

    def update_orders_journal(self, last_order: float) -> bool:
        """Add new order in trade_journal['orders']"""
        if not isinstance(last_order, int | float):
            raise TypeError(
                f"Argument last_order must be 'int' or 'float', not '{type(last_order).__name__}'"
            )
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

    def send_averaging_notify(self, last_order: float) -> bool:
        self.gatekeeper_storage.update_balance()
        balance = self.gatekeeper_storage.get_balance()
        min_sell_price = self.journal.get()["sell_lines"][0]
        min_buy_price = self.journal.get()["buy_lines"][0]

        if not isinstance(last_order, int | float):
            raise TypeError(
                f"Argument last_order must be 'int' or 'float', not '{type(last_order).__name__}'"
            )
        if not balance or balance == {}:
            raise AttributeError("Balance is empty!")
        if not "USDT" in balance.keys():
            raise KeyError('Gatekeeper do not contains key named "USDT"')
        if not isinstance(min_sell_price, float | int):
            raise TypeError(
                f"Sell lines must be list[float], not '{type(min_sell_price).__name__}'"
            )
        if not isinstance(min_buy_price, float | int):
            raise TypeError(
                f"Buy lines must be list[float], not '{type(min_buy_price).__name__}'"
            )
        try:
            logger.info(
                f'Avergaging for ${last_order}. Balance: {balance["USDT"]}. Min price for sell: ${min_sell_price}. Min price for averate: ${min_buy_price}'
            )
            self.telenotify.bought(
                f'```\nAverage price: {last_order} USDT\nBalance: {balance["USDT"]}\nSell line: ${min_sell_price}\nAverage line: ${min_buy_price}```'
            )
        except Exception as e:
            logger.exception(e)
        return True


class Averaging:

    def __init__(
        self,
        lines: LinesManager,
        checkup: Checkup,
        trigger: CrossKlinesTrigger,
        gatekeeper_storage: GatekeeperStorage,
        orders: Orders,
        metamanager: MetaManager,
        notifier: Notifier,
    ) -> None:
        self.lines = lines
        self.checkup = checkup
        self.trigger = trigger
        self.gatekeeper_storage = gatekeeper_storage
        self.orders = orders
        self.metamanager = metamanager
        self.notifier = notifier

    def activate(self) -> bool:
        if self.checkup.valid_balance():
            logger.debug("valid_balance")
            if self.checkup.valid_price():
                logger.debug("valid_price")
                if self.trigger.cross_down_to_up():
                    logger.debug("Trigger cross_down_to_up activated")
                    if self.gatekeeper_storage.update_balance():
                        if self.orders.place_buy_order():
                            logger.info("Buy order placed successfully")
                            time.sleep(2)
                            last_order = self.orders.get_order_history()[0].get(
                                "avgPrice"
                            )
                            logger.debug(f"Last order price: {last_order}")
                            self.checkup.update_orders_journal(float(last_order))
                            logger.debug("Journal updated with new order")
                            self.lines.write_lines(float(last_order))
                            logger.debug("Lines written successfully")
                            self.metamanager.update_all(
                                type="average", value=last_order
                            )
                            logger.debug("Metadata was writed")
                            self.notifier.send_averaging_notify(last_order)
                            return True
