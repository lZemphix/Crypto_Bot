from logging import getLogger
from client.base import Client

logger = getLogger(__name__)


class Klines(Client):

    def __init__(self) -> None:
        self.cnt = 0
        super().__init__()

    def get_klines(self, limit: int = 200) -> dict:
        try:
            kline = self.client.get_kline(
                symbol=self.symbol,
                interval=self.interval,
                limit=limit,
                category="spot",
            )
            self.cnt += 1
            logger.debug(f"Klines req #{self.cnt}")
            return kline["result"]["list"]
        except:
            return None


get_klines = Klines()
