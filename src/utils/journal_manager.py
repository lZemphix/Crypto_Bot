import json
from logging import getLogger

logger = getLogger(__name__)


class JournalManager:

    def get(self) -> dict:
        with open(f"src/data/trade_journal.json") as f:
            journal = json.load(f)
            return journal

    def update(self, data: dict) -> bool:
        with open("src/data/trade_journal.json", "w") as journal:
            json.dump(data, journal, indent=4)
        return True

    def clear(self) -> bool:
        data = dict(laps=0, orders=[], buy_lines=[], sell_lines=[])
        self.update(data)
        return True
