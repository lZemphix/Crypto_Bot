from logging import getLogger
import pandas as pd
from utils.gatekeeper import GatekeeperStorage

logger = getLogger(__name__)


class KlinesManager:

    def __init__(self, gatekeeper_storage: GatekeeperStorage):
        self.gatekeeper_storage = gatekeeper_storage

    def get_klines_dataframe(self) -> pd.DataFrame:
        try:
            klines = self.gatekeeper_storage.get_klines()
            dataframe = pd.DataFrame(klines)
            dataframe.columns = [
                "time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "turnover",
            ]

            dataframe.set_index("time", inplace=True)
            dataframe.index = pd.to_numeric(dataframe.index, downcast="integer").astype(
                "datetime64[ms]"
            )
            dataframe["close"] = pd.to_numeric(dataframe["close"])
            return dataframe
        except ValueError as e:
            logger.error(f"Returned empty dataframe. Message: {e}")
            return pd.DataFrame()
