import time
from client.base import BotBase
from client.orders import get_orders
from logging import getLogger

from config.config import get_bot_config
from utils.gatekeeper import gatekeeper
from utils.journal_manager import JournalManager
from utils.lines_manager import LinesManager
from utils.states import BuyState
from utils.triggers import CrossKlinesTrigger

logger = getLogger(__name__)


class Checkup(BotBase):

    def __init__(self) -> None:
        super().__init__()
        self.trigger = CrossKlinesTrigger()

    def valid_balance(self):
        usdt_balance = gatekeeper.get_balance()["USDT"]
        amount_buy_price = get_bot_config("amountBuy")
        return usdt_balance > amount_buy_price

    def valid_price(self):
        avg_order = get_orders.get_avg_order()
        actual_price = float(gatekeeper.get_klines()[-1][4])
        step_buy = get_bot_config("stepBuy")
        price_lower_than_step = step_buy < (avg_order - actual_price)
        return actual_price < avg_order and price_lower_than_step

    def update_journal(self, last_order: float):
        data = self.journal.get()
        orders = data["orders"]
        orders.append(last_order)
        data["orders"] = orders
        self.journal.update(data)
        return True


class Notifier(Checkup):
    def __init__(self):
        super().__init__()

    def send_averaging_notify(self, last_order: float):
        balance = gatekeeper.get_balance()
        min_sell_price = self.journal.get()["sell_lines"][0]
        min_buy_price = self.journal.get()["buy_lines"][0]
        logger.info(
            f'Avergaging for ${last_order}. Balance: {balance["USDT"]}. Min price for sell: ${min_sell_price}. Min price for averate: ${min_buy_price}'
        )
        self.telenotify.bought(
            f'```\nAvergaging price: {last_order} USDT\nBalance: {balance["USDT"]}\nSell line: ${min_sell_price}\nAverage line: ${min_buy_price}```'
        )


class Averaging(Checkup):

    def __init__(self) -> None:
        super().__init__()
        self.current_state = BuyState.WAITING
        self.lines = LinesManager()

    def activate(self):
        logger.info("Trying to average")
        if self.valid_balance():
            logger.debug("valid_balance")
            if self.valid_price():
                logger.debug("valid_price")
                if self.trigger.cross_down_to_up():
                    logger.debug("Trigger cross_down_to_up activated")
                    if get_orders.place_buy_order():
                        logger.info("Buy order placed successfully")
                        time.sleep(2)
                        last_order = get_orders.get_order_history()[0].get("avgPrice")
                        logger.debug(f"Last order price: {last_order}")
                        if self.update_journal(float(last_order)):
                            logger.debug("Journal updated with new order")
                            if self.lines.write_lines(float(last_order)):
                                logger.debug("Lines written successfully")
                                Notifier().send_averaging_notify(last_order)
                                logger.debug("Notification sent for averaging")
                                return True
