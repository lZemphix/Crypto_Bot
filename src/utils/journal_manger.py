import json
from logging import getLogger

logger = getLogger(__name__)

class JournalManager:
    def __init__(self):
        super().__init__()

    def get(self):
        with open(f'src/src/trade_journal.json') as f:
            journal = json.load(f)
            return journal
        
    def update(self, data: dict):
        with open('src/src/trade_journal.json', 'w') as journal:
            data = json.dump(data, journal, indent=4)
    
    def clear(self):
        data = dict(laps=0, orders=[], buy_lines=[], sell_lines=[])
        self.update(data)
        return True
    
    