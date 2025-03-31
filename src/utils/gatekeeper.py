from client.account import Account
from client.klines import Klines
from logging import getLogger

logger = getLogger(__name__)

class Gatekeeper:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.valid_data = {
                'balance': {}, 
                'klines': []
            }
        return cls._instance

    def get(self) -> dict:
        return self.valid_data

    def update_balance(self) -> bool:
        try: balance = Account().get_balance()
        except: balance = self.get()['balance']
        self.valid_data['balance'] = balance
        return True
    
    def update_klines(self) -> bool:
        try: klines = Klines().get_klines()
        except: klines = self.get()['klines']
        self.valid_data['klines'] = klines
        return True
    
    def get_updated_balance(self):
        try:
            self.update_balance()
        except:
            pass
        return self.get()['balance']
    
    def get_updated_klines(self):
        self.update_klines()
        return self.get()['klines']
    




