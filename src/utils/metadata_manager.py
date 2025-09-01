import enum
import json
import datetime
from logging import getLogger
from utils.journal_manager import JournalManager

logger = getLogger(__name__)


class MetaPreviousTypes(enum.Enum):
    SELL_ACTION: str = "sell_actions"
    BUY_ACTION: str = "buy_actions"


class MetaManager:
    def __init__(self, journal: JournalManager):
        self.journal = journal
        self.path = "metadata.json"

    def get(self) -> dict:
        with open(self.path) as f:
            return json.load(f)

    def update(self, target: str, data) -> None:
        metadata = self.get()
        metadata[target] = data
        with open(self.path, "w") as f:
            json.dump(metadata, f, indent=4)

    def update_last_action(self, type: str) -> bool:
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

    def update_actual(self) -> bool:
        try:
            journal = self.journal.get()
            orders = journal["orders"]
            try:
                closest_s_line = journal["sell_lines"][0]
                closest_a_line = journal["buy_lines"][0]
            except IndexError:
                logger.exception("LinesError! sell or buy lines is empty")
                closest_s_line = 0
                closest_a_line = 0
            data = {
                "orders_amount": len(orders),
                "avg_order_price": sum(orders)
                / (len(orders) if len(orders) != 0 else 1),
                "closest_s_line": closest_s_line,
                "closest_a_line": closest_a_line,
            }
            self.update("actual", data)
        except Exception as e:
            logger.exception(e)
        return True

    def update_previous_actions(self, type: MetaPreviousTypes, value: float | int):
        data = self.get()
        data["previous_actions"][type.value].append(value)
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)

    def update_all(self, type: str, value: float | int = None) -> bool:
        if value:
            pa_type = (
                MetaPreviousTypes.SELL_ACTION
                if type == "sell"
                else MetaPreviousTypes.BUY_ACTION
            )
            self.update_previous_actions(pa_type, value)
        self.update_last_action(type=type)
        self.update_actual()
        return True
