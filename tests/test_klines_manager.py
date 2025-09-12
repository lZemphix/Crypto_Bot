import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.utils.klines_manager import KlinesManager


class TestKlinesManager:

    @pytest.fixture
    def mock_gatekeeper_storage(self):
        return MagicMock()

    def test_get_klines_dataframe(self, mock_gatekeeper_storage):
        klines_manager = KlinesManager(mock_gatekeeper_storage)
        klines = [
            [1622890800000, 2800.0, 2810.0, 2790.0, 2805.0, 1000.0, 1000.0],
            [1622890860000, 2805.0, 2815.0, 2800.0, 2810.0, 2000.0, 2000.0],
        ]
        mock_gatekeeper_storage.get_klines.return_value = klines

        df = klines_manager.get_klines_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert list(df.columns) == [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover",
        ]
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_get_klines_dataframe_empty(self, mock_gatekeeper_storage):
        klines_manager = KlinesManager(mock_gatekeeper_storage)
        mock_gatekeeper_storage.get_klines.return_value = []

        df = klines_manager.get_klines_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert df.empty
