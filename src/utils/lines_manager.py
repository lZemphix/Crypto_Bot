from logging import getLogger
from config.config import get_bot_config
from utils.gatekeeper import Gatekeeper
from utils.journal_manger import JournalManager

logger = getLogger(__name__)

class LinesManager:
    
    def __init__(self):
        self.journal = JournalManager()

    def write_lines(self, order_price: float):
        data = self.journal.get()
        data['sell_lines'], data['buy_lines'] = self.create_lines(order_price)
        self.journal.update(data)
        return True
    
    def create_lines(self, order_price: float):
        """sell buy"""
        sell_lines, buy_lines = [], []
        step_buy =  get_bot_config('stepBuy')
        step_sell = get_bot_config('stepSell')
        orders = self.journal.get()['orders']
        avg_order = sum(orders) / len(orders) if len(orders) != 0 else 1
        for i in range(30):
            sell_lines.append(round(avg_order+step_sell*(i+1), 3))
            buy_lines.append(round(order_price-step_buy*(i+1),3))
        return sell_lines, buy_lines