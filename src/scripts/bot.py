from logging import getLogger
from client.base import BotBase
from client.orders import get_orders
from scripts.averaging import Averaging
from scripts.first_buy import FirstBuy
from scripts.sell import Sell
from utils.gatekeeper import gatekeeper_storage, Gatekeeper
from utils.states import BotState
from utils.metadata_manager import MetaManager
from utils.triggers import BalanceTrigger
from data.consts import *
import time


logger = getLogger(__name__)


def initial_update():
    try:
        logger.debug('enter initial_update')
        if gatekeeper_storage.update_balance():
            if gatekeeper_storage.update_klines():
                logger.debug('out initial_update')
                return True
    except Exception as e:
        logger.error(e)


class Price(BotBase):
    def __init__(self):
        super().__init__()

    def get_price_side(self):
        logger.debug('enter Price.get_price_side')
        avg_order = get_orders.get_avg_order()
        try:
            price = float(gatekeeper_storage.get_klines()[-1][4])
            logger.debug('out Price.get_price_side')
            return round(price - avg_order, 3)
        except TypeError:
            logger.warning("TypeError. Return 0")
            return 0


class Notifier(BotBase):
    def __init__(self):
        super().__init__()

    def send_activate_notify(self):
        logger.debug('enter Notifier.send_activate_notify')
        usdt_balance = round(gatekeeper_storage.get_balance()["USDT"], 3)
        interval = self.interval
        amount_buy = self.amount_buy
        try:
            coin_balance = f"{gatekeeper_storage.get_balance()[self.coin_name]:.10f}"
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
        logger.debug('out Notifier.send_activate_notify')


    def send_nem_notify(self):
        logger.debug('enter Notifier.send_nem_notify')
        usdt_balance = round(gatekeeper_storage.get_balance()["USDT"], 3)
        self.telenotify.warning(
            f"Not enough money!```\nBalance: {usdt_balance}\nMin order price: {self.amount_buy}```"
        )
        logger.warning(
            f"Not enough money! Balance: {usdt_balance}. Min order price: {self.amount_buy}"
        )
        logger.debug('out Notifier.send_nem_notify')



class States(BotBase):

    def __init__(self):
        super().__init__()
        self.balance_trigger = BalanceTrigger()
        self.first_buy = FirstBuy()
        self.averaging = Averaging()
        self.sell = Sell()

    def insufficient_balance_state(self):
        logger.debug('enter States.insufficient_balance_state')
        Notifier().send_nem_notify()
        logger.info("Not enough money for buying, trying to sell")
        while self.balance_trigger.invalid_balance():
            time.sleep(2)
            if self.sell.activate():
                logger.debug("Switching to FIRST_BUY state")
                logger.debug('out States.insufficient_balance_state')
                return BotState.FIRST_BUY

    def waiting_state(self):
        logger.debug('enter States.waiting_state')
        if len(self.journal.get()["orders"]) == 0:
            logger.debug('out States.waiting_state FirstBuy')
            return BotState.FIRST_BUY
        elif Price().get_price_side() > 0:
            logger.debug('out States.waiting_state Sell')
            return BotState.SELL
        else:
            logger.debug('out States.waiting_state Avg')
            return BotState.AVERAGING

    def averaging_state(self):
        logger.debug('enter States.averaging_state')
        if self.averaging.activate():
            gatekeeper_storage.update_balance()
            MetaManager().update_all(type="average")
            logger.info("Averaged. Switching to WAITING state")
        logger.debug('out States.waiting_state')
        return BotState.WAITING

    def sell_state(self):
        logger.debug('enter States.sell_state')
        if self.sell.activate():
            logger.info("Sold. Switching to FIRST_BUY state")
            gatekeeper_storage.update_balance()
            MetaManager().update_all(type="sell")
            logger.debug('out States.sell_state First')
            return BotState.FIRST_BUY
        else:
            logger.debug('out States.sell_state Wait')
            return BotState.WAITING

    def first_buy_state(self):
        logger.debug('enter States.first_buy_state')
        if self.first_buy.activate():
            logger.info("Bought. Switching to WAITING state")
            gatekeeper_storage.update_balance()
            MetaManager().update_all(type="first buy")
            logger.debug('out States.first_buy_state WAITING' )
            return BotState.WAITING
        logger.debug('out States.first_buy_state FIRST_BUY')
        return BotState.FIRST_BUY


class Bot(BotBase):

    def __init__(self):
        super().__init__()

    def activate(self):
        logger.debug('enter Bot.activate')
        Gatekeeper()
        if not initial_update():
            raise SystemExit("Can't do initial update")
        current_state = BotState.WAITING
        Notifier().send_activate_notify()
        logger.info("Bot was activated!")
        while True:
            time.sleep(1)

            if BalanceTrigger().invalid_balance():
                current_state = States().insufficient_balance_state()

            if current_state == BotState.WAITING:
                current_state = States().waiting_state()

            if current_state == BotState.AVERAGING:
                current_state = States().averaging_state()

            if current_state == BotState.SELL:
                current_state = States().sell_state()

            if current_state == BotState.FIRST_BUY:
                current_state = States().first_buy_state()
