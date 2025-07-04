from logging import getLogger
import sys
import pandas as pd
from utils.gatekeeper import Gatekeeper

logger = getLogger(__name__)

class KlinesManager:
    def __init__(self):
        self.gatekeeper = Gatekeeper()

    def get_klines_dataframe(self) -> pd.DataFrame:
        klines = self.gatekeeper.get_updated_klines()
        dataframe = pd.DataFrame(klines)
        try:
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
            sys.exit(0)
        dataframe.set_index("time", inplace=True)
        dataframe.index = pd.to_numeric(dataframe.index, downcast="integer").astype(
            "datetime64[ms]"
        )
        dataframe = dataframe[::-1]
        dataframe["close"] = pd.to_numeric(dataframe["close"])
        return dataframe

    def get_kline_color(self) -> str:
        klines = Gatekeeper.get_updated_klines()
        current_kline = klines[0][4]
        prev_kline = klines[1][4]
        return "RED" if current_kline < prev_kline else "GREEN"
