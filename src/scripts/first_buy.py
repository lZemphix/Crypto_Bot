import time
from utils.journal_manager import JournalManager
from utils.telenotify import Telenotify
from utils.lines_manager import LinesManager
from client.orders import Orders
from utils.metadata_manager import MetaManager
from utils.triggers import IndicatorTrigger
from logging import getLogger
from data.consts import FIRST_BUY_MESSAGE
from utils.gatekeeper import GatekeeperStorage


logger = getLogger(__name__)


class Checkup:

    def __init__(
        self,
        gatekeeper_storage: GatekeeperStorage,
        journal: JournalManager,
        telenotify: Telenotify,
        amount_buy: float,
    ) -> None:
        self.gatekeeper_storage = gatekeeper_storage
        self.journal = journal
        self.amount_buy = amount_buy
        self.telenotify = telenotify

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

    def valid_balance(self) -> bool:
        balance = self.gatekeeper_storage.get_balance()["USDT"]
        if not isinstance(balance, int | float):
            raise TypeError(
                f"Balance have a invalid type. Must be 'int' or 'float', not '{type(balance).__name__}'"
            )
        if not isinstance(self.amount_buy, float):
            raise TypeError(
                f"configs param have a invalid type. Must be 'float', not '{type(self.amount_buy).__name__}'"
            )

        return balance > self.amount_buy


class Notifier:
    def __init__(
        self,
        telenotify: Telenotify,
        gatekeeper_storage: GatekeeperStorage,
        journal: JournalManager,
    ):
        self.telenotify = telenotify
        self.gatekeeper_storage = gatekeeper_storage
        self.journal = journal

    def send_buy_notify(self, last_order: float) -> None:
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
                f"First buy for ${last_order}. Balance: {balance["USDT"]}. Min price for sell: ${min_sell_price}. Min price for averate: ${min_buy_price}"
            )
            self.telenotify.bought(
                FIRST_BUY_MESSAGE.format(
                    buy_price=last_order,
                    balance=balance["USDT"],
                    sell_line=min_sell_price,
                    buy_line=min_buy_price,
                )
            )
        except Exception as e:
            logger.exception(e)
        return True


class FirstBuy:

    def __init__(
        self,
        checkup: Checkup,
        trigger: IndicatorTrigger,
        gatekeeper_storage: GatekeeperStorage,
        orders: Orders,
        lines: LinesManager,
        metamanager: MetaManager,
        notifier: Notifier,
    ) -> None:
        self.checkup = checkup
        self.trigger = trigger
        self.gatekeeper_storage = gatekeeper_storage
        self.orders = orders
        self.lines = lines
        self.metamanager = metamanager
        self.notifier = notifier

    def activate(self) -> bool:
        if self.checkup.valid_balance():
            logger.info("valid_balance")
            if self.trigger.rsi_trigger():
                logger.debug("rsi trigger")
                if self.gatekeeper_storage.update_balance():
                    if self.orders.place_buy_order():
                        logger.info("Buy order placed successfully")
                        time.sleep(2)
                        last_order = float(
                            self.orders.get_order_history()[0].get("avgPrice")
                        )
                        self.checkup.update_orders_journal(last_order)
                        logger.debug("Journal updated with new order")
                        self.lines.write_lines(last_order)
                        logger.debug("Lines written successfully")
                        self.notifier.send_buy_notify(last_order)
                        logger.debug("Notification sent for first buy")
                        self.metamanager.update_all(type="first_buy", value=last_order)
                        logger.debug("Metadata was writed")
                        return True
