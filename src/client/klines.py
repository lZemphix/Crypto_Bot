from logging import getLogger
from pybit.unified_trading import HTTP

logger = getLogger(__name__)


class Klines:

    def __init__(self, client: HTTP, symbol: str, interval: int) -> None:
        self.client = client
        self.symbol = symbol
        self.interval = interval

    def get_klines(self, limit: int = 200) -> dict:
        """returns klines dict like {[timetsamp, open, high, low, close, volume, turnover]}"""
        try:
            kline = self.client.get_kline(
                symbol=self.symbol,
                interval=self.interval,
                limit=limit,
                category="spot",
            )
            return kline["result"]["list"]
        except Exception as e:
            logger.exception(f"getting klines error! Message: {e}")
            return None
