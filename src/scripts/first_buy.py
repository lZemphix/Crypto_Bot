import time
from utils.lines_manager import LinesManager
from utils.states import BuyState
from client.base import BotBase
from client.orders import Orders
from utils.triggers import IndicatorTrigger
from logging import getLogger
from data.consts import FIRST_BUY_MESSAGE
from utils.gatekeeper import gatekeeper
from utils.journal_manager import JournalManager


logger = getLogger(__name__)


class Checkup(BotBase):

    def __init__(self):
        super().__init__()
        self.journal = JournalManager()

    def update_journal(self, last_order: float) -> None:
        data = self.journal.get()
        orders = data["orders"]
        orders.append(last_order)
        data["orders"] = orders
        self.journal.update(data)

    def valid_balance(self) -> None:
        return gatekeeper.get_balance()["USDT"] > self.amount_buy


class Notifier(Checkup):
    def __init__(self):
        super().__init__()

    def send_notify(self, last_order: float) -> None:
        balance = gatekeeper.get_balance()["USDT"]
        min_sell_price = self.journal.get()["sell_lines"][0]
        min_buy_price = self.journal.get()["buy_lines"][0]

        logger.info(
            f"First buy for ${last_order}. Balance: {balance}. Min price for sell: ${min_sell_price}. Min price for averate: ${min_buy_price}"
        )
        self.telenotify.bought(
            FIRST_BUY_MESSAGE.format(
                buy_price=last_order,
                balance=balance,
                sell_line=min_sell_price,
                buy_line=min_buy_price,
            )
        )

    def nem_notify(self) -> None:
        usdt_balance = round(gatekeeper.get_balance()["USDT"], 3)
        amount_buy = self.amount_buy
        self.telenotify.warning(
            f"Not enough money!```\nBalance: {usdt_balance}\nMin order price: {amount_buy}```"
        )


class FirstBuy(Checkup):


    def __init__(self):
        super().__init__()
        self.orders = Orders()
        self.trigger = IndicatorTrigger()
        self.current_state = BuyState.WAITING
        self.lines = LinesManager()


    def activate(self) -> bool:
        logger.info("Trying to do first buy")
        if self.current_state == BuyState.PRICE_CORRECT:
            logger.debug("State: PRICE_CORRECT")
            if self.orders.place_buy_order():
                logger.info("Buy order placed successfully")
                time.sleep(2)
                last_order = float(self.orders.get_order_history()[0].get("avgPrice"))
                logger.debug(f"Last order price: {last_order}")
                if self.lines.write_lines(last_order):
                    logger.debug("Lines written successfully")
                    Notifier().send_notify(last_order)
                    logger.debug("Notification sent for first buy")
                    self.update_journal(last_order)
                    logger.debug("Journal updated with new order")
                    self.current_state = BuyState.STOPPED
                    return True

        if (
            self.trigger.rsi_trigger() and 
            self.current_state == BuyState.BALANCE_CORRECT
        ):
            logger.debug("RSI trigger activated, switching to PRICE_CORRECT state")
            self.current_state = BuyState.PRICE_CORRECT
            logger.debug("State now: %s", self.current_state)

        if (self.valid_balance() and 
            self.current_state == BuyState.WAITING
        ):
            logger.debug("Balance valid, switching to BALANCE_CORRECT state")
            self.current_state = BuyState.BALANCE_CORRECT
            logger.debug("State now: %s", self.current_state)
