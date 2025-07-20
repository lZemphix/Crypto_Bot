from logging import getLogger
from client.base import Client

logger = getLogger(__name__)


class Klines(Client):

    def __init__(self) -> None:
        super().__init__()

    def get_klines(self, limit: int = 200) -> dict:
        try:
            kline = self.client.get_kline(
                symbol=self.symbol,
                interval=self.interval,
                limit=limit,
                category="spot",
            )
            return kline["result"]["list"]
        except Exception as e:
            logger.warning("Getting klines error! Message: %s", e)
            return None


get_klines = Klines()
