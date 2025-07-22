from logging import getLogger
import pandas as pd
from utils.gatekeeper import gatekeeper_storage

logger = getLogger(__name__)


class KlinesManager:
    def __init__(self):
        pass

    def get_klines_dataframe(self) -> pd.DataFrame:
        try:
            klines = gatekeeper_storage.get_klines()
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
        except ValueError as e:
            logger.error("Returned empty dataframe. Message: %s", e)
            return pd.DataFrame()
        dataframe.set_index("time", inplace=True)
        dataframe.index = pd.to_numeric(dataframe.index, downcast="integer").astype(
            "datetime64[ms]"
        )
        dataframe["close"] = pd.to_numeric(dataframe["close"])
        return dataframe
