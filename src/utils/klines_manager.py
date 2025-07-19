from logging import getLogger
import pandas as pd
from utils.gatekeeper import gatekeeper

logger = getLogger(__name__)


class KlinesManager:
    def __init__(self):
        pass

    def get_klines_dataframe(self) -> pd.DataFrame:
        try:
            klines = gatekeeper.get_updated_klines()
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
            logger.error(e)
            return pd.DataFrame()
        dataframe.set_index("time", inplace=True)
        dataframe.index = pd.to_numeric(dataframe.index, downcast="integer").astype(
            "datetime64[ms]"
        )
        dataframe = dataframe[::-1]
        dataframe["close"] = pd.to_numeric(dataframe["close"])
        return dataframe
