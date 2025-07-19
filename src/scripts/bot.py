from logging import getLogger
import time

from scripts.averaging import Averaging
from scripts.sell import Sell
from utils.gatekeeper import gatekeeper
from utils.journal_manager import JournalManager
from utils.states import BotState
from client.base import BotBase
from scripts.first_buy import FirstBuy
from utils.klines_manager import KlinesManager
from utils.telenotify import Telenotify
from data.consts import *
from utils.triggers import BalanceTrigger


logger = getLogger(__name__)


class Price(BotBase):
    def __init__(self):
        super().__init__()
        self.journal = JournalManager()

    def price_side(self):
        orders = self.journal.get()["orders"]
        avg_order = sum(orders) / (len(orders) if len(orders) != 0 else 1)
        try:
            price = float(gatekeeper.get_updated_klines()[0][4])
            return round(price - avg_order, 3)
        except TypeError:
            logger.warning("TypeError. Return 0")
            return 0


class Notifications(BotBase):
    def __init__(self):
        super().__init__()
        self.journal = JournalManager()

    def activate_message(self):
        usdt_balance = round(gatekeeper.get_updated_balance()["USDT"], 3)
        interval = self.interval
        amount_buy = self.amount_buy
        try:
            coin_balance = f"{gatekeeper.get_updated_balance()[self.coin_name]:.10f}"
        except:
            coin_balance = 0.00
        self.telenotify.bot_status(
            BOT_STARTED_MESSAGE.format(
                symbol=self.symbol,
                usdt_balance=usdt_balance,
                coin_name=self.coin_name,
                coin_balance=coin_balance,
                interval=interval,
                amount_buy=amount_buy,
            )
        )

    def nem_notify(self):
        usdt_balance = round(gatekeeper.get_updated_balance()["USDT"], 3)
        amount_buy = self.amount_buy
        self.telenotify.warning(
            f"Not enough money!```\nBalance: {usdt_balance}\nMin order price: {amount_buy}```"
        )
        logger.warning(
            f"Not enough money! Balance: {usdt_balance}. Min order price: {amount_buy}"
        )


class Bot(BotBase):

    def __init__(self):
        super().__init__()
        self.current_state = BotState.WAITING
        self.klines = KlinesManager()
        self.journal = JournalManager()
        self.balance_trigger = BalanceTrigger()

    def activate(self):
        logger.info("Bot activation started")
        Notifications().activate_message()
        while self.current_state != BotState.STOPPED:
            time.sleep(0.5)
            logger.debug(f"Current state: {self.current_state}")
            if self.balance_trigger.invalid_balance():
                self.nem_notify()
                logger.info("State: sell")
                while self.balance_trigger.invalid_balance():
                    logger.debug("Not enough money for buying, switching to SELL state")
                    self.current_state = BotState.SELL
                    if Sell().activate():
                        logger.info("Sold successful, switching to FIRST_BUY state")
                        self.current_state = BotState.FIRST_BUY

            if self.current_state == BotState.WAITING:
                logger.debug("State: WAITING")
                if len(self.journal.get()["orders"]) == 0:
                    logger.info("No orders, setting FIRST_BUY state")
                    self.current_state = BotState.FIRST_BUY
                elif Price().price_side() > 0:
                    logger.info("Coin price > 0. Switching to SELL state")
                    self.current_state = BotState.SELL
                else:
                    logger.info("Coin price < 0. Switching to AVERAGING state")
                    self.current_state = BotState.AVERAGING

            if self.current_state == BotState.AVERAGING:
                if Averaging().activate():
                    logger.info("Averaging activated, switching to WAITING state")
                    self.current_state = BotState.WAITING
                else:
                    logger.info("Averaging not activated, staying in WAITING state")
                    self.current_state = BotState.WAITING

            if self.current_state == BotState.SELL:
                logger.info("State: SELL")
                if Sell().activate():
                    logger.info("Sell activated, switching to FIRST_BUY state")
                    self.current_state = BotState.FIRST_BUY
                else:
                    logger.info("Sell not activated, switching to WAITING state")
                    self.current_state = BotState.WAITING

            if self.current_state == BotState.FIRST_BUY:
                logger.info("State: FIRST_BUY")
                if FirstBuy().activate():
                    logger.info("Bought, switching to WAITING state")
                    self.current_state = BotState.WAITING
