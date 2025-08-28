from unittest.mock import patch
import pandas as pd
from utils.klines_manager import KlinesManager


def test_get_klines_dataframe_success():
    mock_klines = [
        [1672531200000, "100", "110", "90", "105", "1000", "105000"],
        [1672534800000, "105", "115", "100", "110", "1200", "132000"],
    ]
    with patch("utils.klines_manager.gatekeeper_storage") as mock_gatekeeper:
        mock_gatekeeper.get_klines.return_value = mock_klines
        km = KlinesManager()
        df = km.get_klines_dataframe()
        assert not df.empty
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (2, 6)
        assert list(df.columns) == [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover",
        ]
        assert df.index.dtype == "datetime64[ms]"
        assert pd.api.types.is_numeric_dtype(df["close"])


def test_get_klines_dataframe_empty():
    with patch("utils.klines_manager.gatekeeper_storage") as mock_gatekeeper:
        mock_gatekeeper.get_klines.return_value = []
        km = KlinesManager()
        df = km.get_klines_dataframe()
        assert df.empty
        assert isinstance(df, pd.DataFrame)
