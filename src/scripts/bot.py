from logging import getLogger

from scripts.averaging import Averaging
from scripts.sell import Sell
from utils.gatekeeper import Gatekeeper
from utils.journal_manger import JournalManager
from utils.states import BotState
from client.bases import BotBase
from scripts.first_buy import FirstBuy
from utils.klines_manager import KlinesManager
from utils.telenotify import TeleNotify
from src.consts import *


logger = getLogger(__name__)

class Bot(BotBase):

    def __init__(self):
        super().__init__()
        self.current_state = BotState.WAITING
        self.transitions = BotState.transitions()
        self.klines = KlinesManager()
        self.journal = JournalManager()
        self.gatekeeper = Gatekeeper()
    
    def price_side(self):
        orders = self.journal.get()['orders']
        avg_order = sum(orders)/len(orders) if len(orders) != 0 else 1
        price = float(self.gatekeeper.get_updated_klines()[0][4])
        return price-avg_order
    
    def activate_message(self):
        usdt_balance = round(self.gatekeeper.get_updated_balance()['USDT'],3)
        interval = self.interval
        amount_buy = self.amount_buy
        try:
            coin_balance = round(self.gatekeeper.get_updated_balance()[self.coin_name],3)
        except:
            coin_balance = 0.00
        TeleNotify().bot_status(BOT_STARTED_MESSAGE.format(symbol=self.symbol, usdt_balance=usdt_balance, 
                                                           coin_name=self.coin_name, coin_balance=coin_balance,
                                                           interval=interval, amount_buy=amount_buy))

    def activate(self):
        self.activate_message()
        while self.current_state != BotState.STOPPED:
            logger.info('current state: %s', self.current_state)
            
            if self.current_state == BotState.WAITING:

                if len(self.journal.get()['orders']) == 0:
                    self.current_state = BotState.FIRST_BUY
                elif self.price_side() > 0:
                    self.current_state = BotState.SELL
                else:
                    self.current_state = BotState.AVERAGING

            elif self.current_state == BotState.AVERAGING:
                if Averaging().activate():
                    self.current_state = BotState.WAITING
            
            elif self.current_state == BotState.SELL:
                if Sell().activate():
                    self.current_state = BotState.FIRST_BUY
            
            elif self.current_state == BotState.FIRST_BUY:
                if FirstBuy().activate():
                    self.current_state = BotState.WAITING

