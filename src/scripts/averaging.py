from client.bases import BotBase
from client.orders import Orders    
from logging import getLogger

from config.config import get_bot_config
from utils.gatekeeper import Gatekeeper
from utils.klines_manager import KlinesManager
from utils.journal_manger import JournalManager
from utils.lines_manager import LinesManager
from utils.states import BuyState
from utils.triggers import CrossKlinesTrigger

logger = getLogger(__name__)

class Averaging(BotBase):

    def __init__(self) -> None:
        super().__init__()
        self.klines = KlinesManager()
        self.orders = Orders()
        self.gatekeeper = Gatekeeper()
        self.journal = JournalManager()
        self.lines = LinesManager()
        self.trigger = CrossKlinesTrigger()
        self.current_state = BuyState.WAITING
        self.transitions = BuyState.transitions()

    def get_avg_order(self):
        orders = self.journal.get()['orders']
        return (sum(orders) / len(orders)) if len(orders) > 0 else 0
    
    def valid_balance(self):
        usdt_balance = self.gatekeeper.get_updated_balance()['USDT']
        amount_buy_price = get_bot_config('amountBuy')
        return usdt_balance > amount_buy_price
    
    def valid_price(self):
        avg_order = self.get_avg_order()
        actual_price = float(self.gatekeeper.get_updated_klines()[0][4])
        step_buy = get_bot_config('stepBuy')
        logger.info('price diff: %s, strp_buy: %s', (avg_order - actual_price), step_buy)
        price_lower_than_step = step_buy < (avg_order - actual_price)
        return (actual_price < avg_order and price_lower_than_step)

    def send_notify_(self, last_order: float):
        balance = self.gatekeeper.get_updated_balance()
        min_sell_price = self.journal.get()['sell_lines'][0]
        min_buy_price = self.journal.get()['buy_lines'][0]
        logger.info(f'Avergaging for ${last_order}. Balance: {balance["USDT"]}. Min price for sell: ${min_sell_price}. Min price for averate: ${min_buy_price}')
        self.notify.bought(f'Avergaging for ${last_order}\nBalance: {balance["USDT"]}\nMin price for sell: ${min_sell_price}\nMin price for averate: ${min_buy_price}')

    def update_journal(self, last_order: float):
        data = self.journal.get()
        orders = data['orders']
        orders.append(last_order)
        data['orders'] = orders
        self.journal.update(data)
        return True

    def activate(self):
        if self.valid_balance():
            logger.info('valid_balance')
            if self.valid_price():
                logger.info('valid_price')
                if self.trigger.cross_down_to_up():
                    if self.orders.place_buy_order():
                        last_order = self.orders.get_order_history()[0].get('avgPrice')
                        if self.update_journal(float(last_order)):
                            if self.lines.write_lines(float(last_order)-self.stepBuy):
                                self.send_notify_(last_order)
                                return True