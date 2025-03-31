from utils.lines_manager import LinesManager
from utils.states import BuyState
from client.bases import BotBase
from client.orders import Orders
from client.klines import Klines
from utils.telenotify import TeleNotify
from utils.triggers import IndicatorTrigger
from logging import getLogger
from src.consts import FIRST_BUY_MESSAGE
from utils.gatekeeper import Gatekeeper
from utils.journal_manger import JournalManager


logger = getLogger(__name__)

class FirstBuy(BotBase):
    
    def __init__(self):
        super().__init__()
        self.orders = Orders()
        self.klines = Klines()
        self.trigger = IndicatorTrigger()
        self.gatekeeper = Gatekeeper()
        self.journal = JournalManager()
        self.current_state = BuyState.WAITING
        self.notify = TeleNotify()
        self.lines = LinesManager()
        
    def valid_balance(self):
        return self.gatekeeper.get_updated_balance()['USDT'] > self.amount_buy

    def send_notify_(self, last_order: float):
        balance = self.gatekeeper.get_updated_balance()
        min_sell_price = self.journal.get()['sell_lines'][0]
        min_buy_price = self.journal.get()['buy_lines'][0]
        
        logger.info(f'First buy for ${last_order}. Balance: {balance["USDT"]}. Min price for sell: ${min_sell_price}. Min price for averate: ${min_buy_price}')
        self.notify.bought(FIRST_BUY_MESSAGE.format(buy_price=last_order))

    def update_journal(self, last_order: float):
        data = self.journal.get()
        orders = data['orders']
        orders.append(last_order)
        data['orders'] = orders
        self.journal.update(data)

    def activate(self) -> bool:
        logger.info('first')
        while self.current_state != BuyState.STOPPED:
            if self.current_state == BuyState.PRICE_CORRECT:
                if self.orders.place_buy_order():
                    last_order = float(self.orders.get_order_history()[0].get('avgPrice'))
                    print(last_order)
                    if self.lines.write_lines(last_order): 
                        self.send_notify_(last_order)
                        self.update_journal(last_order)
                        self.current_state = BuyState.STOPPED
                        return True

            if self. trigger.rsi_trigger() and self.current_state == BuyState.BALANCE_CORRECT:
                self.current_state = BuyState.PRICE_CORRECT
                logger.info('State now: %s', self.current_state)

            if self.valid_balance() and self.current_state == BuyState.WAITING:
                self.current_state = BuyState.BALANCE_CORRECT
                logger.info('State now: %s', self.current_state)

      