import json
import datetime
from logging import getLogger
from utils.journal_manager import JournalManager

logger = getLogger(__name__)


class MetaManager:
    def __init__(self, journal: JournalManager):
        self.journal = journal
        self.path = "metadata.json"

    def get(self) -> dict:
        with open(self.path) as f:
            return json.load(f)

    def update(self, target: str, data: str | float) -> None:
        metadata = self.get()
        metadata[target] = data
        with open(self.path, "w") as f:
            json.dump(metadata, f, indent=4)

    def update_last_action(self, type: str) -> None:
        try:
            date = datetime.datetime.now(datetime.UTC)
            data = {
                "type": type,
                "date": datetime.datetime.strftime(date, "%Y-%m-%d %H:%M:%S"),
            }
            self.update("last_action", data)
        except Exception as e:
            logger.exception(e)
        return True

    def update_actual(self) -> None:
        try:
            orders = self.journal.get()["orders"]
            data = {
                "orders_amount": len(orders),
                "avg_order_price": sum(orders)
                / (len(orders) if len(orders) != 0 else 1),
                "closest_s_line": self.journal.get()["sell_lines"][0],
                "closest_a_line": self.journal.get()["buy_lines"][0],
            }
            self.update("actual", data)
        except Exception as e:
            logger.exception(e)
        return True

    def update_all(self, type: str) -> bool:
        self.update_last_action(type=type)
        self.update_actual()
        return True
