from logging import getLogger
from config.config import bot_settings, env_settings
from client.orders import Orders
from scripts.averaging import Averaging
from scripts.first_buy import FirstBuy
from scripts.sell import Sell
from utils.journal_manager import JournalManager
from utils.telenotify import Telenotify
from utils.gatekeeper import Gatekeeper, GatekeeperStorage
from utils.states import BotState
from utils.triggers import BalanceTrigger
from data.consts import *
import time


logger = getLogger(__name__)


def initial_update(gatekeeper_storage: GatekeeperStorage):
    try:
        logger.debug("enter initial_update")
        if gatekeeper_storage.update_balance():
            if gatekeeper_storage.update_klines():
                logger.debug("out initial_update")
                return True
    except Exception as e:
        logger.error(e)


class Price:
    def __init__( 
        self, 
        orders: Orders, 
        gatekeeper_storage: GatekeeperStorage
        ) -> None:
        self.orders = orders
        self.gatekeeper_storage = gatekeeper_storage

    def get_price_side(self):
        logger.debug("enter Price.get_price_side")
        avg_order = self.orders.get_avg_order()
        try:
            price = float(self.gatekeeper_storage.get_klines()[-1][4])
            logger.debug("out Price.get_price_side")
            return round(price - avg_order, 3)
        except TypeError:
            logger.warning("TypeError. Return 0")
            return 0


class Notifier:
    def __init__( 
        self, 
        gatekeeper_storage: GatekeeperStorage,
        telenotify: Telenotify,
        interval: int,
        amount_buy: float,
        symbol: str,
        coin_name: str
        ):
        self.gatekeeper_storage = gatekeeper_storage
        self.interval = interval
        self.amount_buy = amount_buy
        self.telenotify = telenotify
        self.symbol = symbol
        self.coin_name = coin_name

    def send_activate_notify(self):
        logger.debug("enter Notifier.send_activate_notify")
        usdt_balance = round(self.gatekeeper_storage.get_balance()["USDT"], 3)
        interval = self.interval
        amount_buy = self.amount_buy
        try:
            coin_balance = f"{self.gatekeeper_storage.get_balance()[self.coin_name]:.10f}"
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
        logger.debug("out Notifier.send_activate_notify")

    def send_nem_notify(self):
        logger.debug("enter Notifier.send_nem_notify")
        usdt_balance = round(self.gatekeeper_storage.get_balance()["USDT"], 3)
        self.telenotify.warning(
            f"Not enough money!```\nBalance: {usdt_balance}\nMin order price: {self.amount_buy}```"
        )
        logger.warning(
            f"Not enough money! Balance: {usdt_balance}. Min order price: {self.amount_buy}"
        )
        logger.debug("out Notifier.send_nem_notify")


class States:

    def __init__(self,
        balance_trigger: BalanceTrigger,
        first_buy: FirstBuy,
        averaging: Averaging,
        sell: Sell,
        notifier: Notifier,
        journal: JournalManager,
        price: Price,
        gatekeeper_storage: GatekeeperStorage
        ) -> None:
        self.balance_trigger = balance_trigger
        self.first_buy = first_buy
        self.averaging = averaging
        self.sell = sell
        self.notifier = notifier
        self.journal = journal
        self.price = price
        self.gatekeeper_storage = gatekeeper_storage

    def insufficient_balance_state(self):
        logger.debug("enter States.insufficient_balance_state")
        self.notifier.send_nem_notify()
        logger.info("Not enough money for buying, trying to sell")
        while self.balance_trigger.invalid_balance():
            time.sleep(2)
            if self.sell.activate():
                logger.debug("Switching to FIRST_BUY state")
                logger.debug("out States.insufficient_balance_state")
                return BotState.FIRST_BUY

    def waiting_state(self):
        logger.debug("enter States.waiting_state")
        if len(self.journal.get()["orders"]) == 0:
            logger.debug("out States.waiting_state FirstBuy")
            return BotState.FIRST_BUY
        elif self.price.get_price_side() > 0:
            logger.debug("out States.waiting_state Sell")
            return BotState.SELL
        else:
            logger.debug("out States.waiting_state Avg")
            return BotState.AVERAGING

    def averaging_state(self):
        logger.debug("enter States.averaging_state")
        if self.averaging.activate():
            self.gatekeeper_storage.update_balance()
            logger.info("Averaged. Switching to WAITING state")
        logger.debug("out States.waiting_state")
        return BotState.WAITING

    def sell_state(self):
        logger.debug("enter States.sell_state")
        if self.sell.activate():
            logger.info("Sold. Switching to FIRST_BUY state")
            self.gatekeeper_storage.update_balance()
            logger.debug("out States.sell_state First")
            return BotState.FIRST_BUY
        else:
            logger.debug("out States.sell_state Wait")
            return BotState.WAITING

    def first_buy_state(self):
        logger.debug("enter States.first_buy_state")
        if self.first_buy.activate():
            logger.info("Bought. Switching to WAITING state")
            self.gatekeeper_storage.update_balance()
            logger.debug("out States.first_buy_state WAITING")
            return BotState.WAITING
        logger.debug("out States.first_buy_state FIRST_BUY")
        return BotState.FIRST_BUY


class Bot:

    def __init__(
        self,
        notifier: Notifier,
        states: States,
        balance_trigger: BalanceTrigger,
        gatekeeper: Gatekeeper,
        gatekeeper_storage: GatekeeperStorage
        ) -> None:
        self.current_state = BotState.WAITING
        self.notifier = notifier
        self.states = states
        self.balance_trigger = balance_trigger
        self.gatekeeper = gatekeeper
        self.gatekeeper_storage = gatekeeper_storage

    def activate(self):
        logger.debug("enter Bot.activate")
        self.gatekeeper 
        if not initial_update(self.gatekeeper_storage):
            raise SystemExit("Can't do initial update")
        self.notifier.send_activate_notify()
        logger.info("Bot was activated!")

        while True:
            time.sleep(1)

            if self.balance_trigger.invalid_balance():
                current_state = self.states.insufficient_balance_state()

            if current_state == BotState.WAITING:
                current_state = self.states.waiting_state()

            if current_state == BotState.AVERAGING:
                current_state = self.states.averaging_state()

            if current_state == BotState.SELL:
                current_state = self.states.sell_state()

            if current_state == BotState.FIRST_BUY:
                current_state = self.states.first_buy_state()
