from logging import getLogger
from config.config import bot_settings, env_settings
from client.orders import Orders
from scripts.averaging import Averaging
from scripts.first_buy import FirstBuy
from scripts.sell import Sell

from scripts.first_buy import Checkup as FBCheckup
from scripts.averaging import Checkup as AVGCheckup
from scripts.sell import Checkup as SCheckup

from scripts.first_buy import Notifier as FBNotifier
from scripts.averaging import Notifier as AVGNotifier
from scripts.sell import Notifier as SNotifier

from utils.journal_manager import JournalManager
from utils.telenotify import Telenotify
from utils.gatekeeper import Gatekeeper, GatekeeperStorage
from utils.states import BotState
from utils.triggers import BalanceTrigger, IndicatorTrigger, CrossKlinesTrigger
from data.consts import *
import time
from client.klines import Klines
from utils.klines_manager import KlinesManager
from utils.lines_manager import LinesManager
from utils.metadata_manager import MetaManager


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
    def __init__(self, orders: Orders, gatekeeper_storage: GatekeeperStorage) -> None:
        self.orders = orders
        self.gatekeeper_storage = gatekeeper_storage

    def get_price_side(self):
        logger.debug("enter Price.get_price_side")
        avg_order = self.orders.get_avg_order()
        try:
            price = float(self.gatekeeper_storage.get_klines()[-1][4])
            logger.debug("out Price.get_price_side")
            return round(price - avg_order, 3)
        except (TypeError, ValueError):
            logger.warning("TypeError or ValueError. Return 0")
            return 0


class Notifier:
    def __init__(
        self,
        gatekeeper_storage: GatekeeperStorage,
        telenotify: Telenotify,
        interval: int,
        amount_buy: float,
        symbol: str,
        coin_name: str,
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
            coin_balance = (
                f"{self.gatekeeper_storage.get_balance()[self.coin_name]:.10f}"
            )
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
            f"Not enough money!```\nBalance: {usdt_balance}\nMin order price: {self.amount_buy}"
        )
        logger.warning(
            f"Not enough money! Balance: {usdt_balance}. Min order price: {self.amount_buy}"
        )
        logger.debug("out Notifier.send_nem_notify")


class States:

    def __init__(
        self,
        balance_trigger: BalanceTrigger,
        first_buy: FirstBuy,
        averaging: Averaging,
        sell: Sell,
        notifier: Notifier,
        journal: JournalManager,
        price: Price,
        gatekeeper_storage: GatekeeperStorage,
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
        gatekeeper_storage: GatekeeperStorage,
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
                self.current_state = self.states.insufficient_balance_state()

            if self.current_state.value == BotState.WAITING.value:
                self.current_state = self.states.waiting_state()

            if self.current_state.value == BotState.AVERAGING.value:
                self.current_state = self.states.averaging_state()

            if self.current_state.value == BotState.SELL.value:

                self.current_state = self.states.sell_state()

            if self.current_state.value == BotState.FIRST_BUY.value:
                self.current_state = self.states.first_buy_state()


def activate():
    bot_config = bot_settings
    env_config = env_settings

    client = env_config.get_client
    journal_manager = JournalManager()
    telenotify = Telenotify(status=bot_config.send_notify)

    klines_client = Klines(
        client=client, symbol=bot_config.symbol, interval=bot_config.interval
    )
    gatekeeper_storage = GatekeeperStorage(
        klines=klines_client, client=client, account_type=env_config.ACCOUNT_TYPE
    )

    gatekeeper = Gatekeeper(
        gatekeeper_storage=gatekeeper_storage,
        symbol=bot_config.symbol,
        interval=bot_config.interval,
    )

    orders = Orders(
        client=client,
        symbol=bot_config.symbol,
        journal=journal_manager,
        gatekeeper_storage=gatekeeper_storage,
        amount_buy=bot_config.amountBuy,
    )

    klines_manager = KlinesManager(gatekeeper_storage=gatekeeper_storage)

    lines_manager = LinesManager(journal=journal_manager)
    meta_manager = MetaManager(journal=journal_manager)

    balance_trigger = BalanceTrigger(
        gatekeeper_storage=gatekeeper_storage, amount_buy=bot_config.amountBuy
    )
    indicator_trigger = IndicatorTrigger(
        RSI=bot_config.RSI, klines_manager=klines_manager
    )
    cross_klines_trigger = CrossKlinesTrigger(
        gatekeeper_storage=gatekeeper_storage, journal_manager=journal_manager
    )

    price = Price(orders=orders, gatekeeper_storage=gatekeeper_storage)

    first_buy_checkup = FBCheckup(
        gatekeeper_storage=gatekeeper_storage,
        journal=journal_manager,
        telenotify=telenotify,
        amount_buy=bot_config.amountBuy,
    )
    first_buy_notifier = FBNotifier(
        telenotify=telenotify,
        gatekeeper_storage=gatekeeper_storage,
        journal=journal_manager,
    )
    first_buy = FirstBuy(
        checkup=first_buy_checkup,
        trigger=indicator_trigger,
        gatekeeper_storage=gatekeeper_storage,
        orders=orders,
        lines=lines_manager,
        metamanager=meta_manager,
        notifier=first_buy_notifier,
    )

    averaging_checkup = AVGCheckup(
        gatekeeper_storage=gatekeeper_storage,
        orders=orders,
        journal=journal_manager,
        amount_buy=bot_config.amountBuy,
        step_buy=bot_config.stepBuy,
    )
    averaging_notifier = AVGNotifier(
        telenotify=telenotify,
        gatekeeper_storage=gatekeeper_storage,
        journal=journal_manager,
    )
    averaging = Averaging(
        lines=lines_manager,
        checkup=averaging_checkup,
        trigger=cross_klines_trigger,
        gatekeeper_storage=gatekeeper_storage,
        orders=orders,
        metamanager=meta_manager,
        notifier=averaging_notifier,
    )

    sell_checkup = SCheckup(
        gatekeeper_storage=gatekeeper_storage,
        orders=orders,
        step_sell=bot_config.stepSell,
    )
    sell_notifier = SNotifier(
        telenotify=telenotify,
        coin_name=bot_config.symbol.replace("USDT", ""),
        gatekeeper_storage=gatekeeper_storage,
        orders=orders,
    )
    sell = Sell(
        journal=journal_manager,
        trigger=cross_klines_trigger,
        checkup=sell_checkup,
        gatekeeper_storage=gatekeeper_storage,
        orders=orders,
        notifier=sell_notifier,
        metamanager=meta_manager,
    )

    main_notifier = Notifier(
        gatekeeper_storage=gatekeeper_storage,
        telenotify=telenotify,
        interval=bot_config.interval,
        amount_buy=bot_config.amountBuy,
        symbol=bot_config.symbol,
        coin_name=bot_config.symbol.replace(
            "USDT", ""
        ),  # Assuming coin_name can be derived this way
    )

    states = States(
        balance_trigger=balance_trigger,
        first_buy=first_buy,
        averaging=averaging,
        sell=sell,
        notifier=main_notifier,
        journal=journal_manager,
        price=price,
        gatekeeper_storage=gatekeeper_storage,
    )

    bot = Bot(
        notifier=main_notifier,
        states=states,
        balance_trigger=balance_trigger,
        gatekeeper=gatekeeper,
        gatekeeper_storage=gatekeeper_storage,
    )

    bot.activate()
