import pytest
from unittest.mock import MagicMock, patch
from src.utils.triggers import IndicatorTrigger, CrossKlinesTrigger, BalanceTrigger


class TestIndicatorTrigger:

    @pytest.fixture
    def mock_klines_manager(self):
        return MagicMock()

    @patch("src.utils.triggers.ta.momentum.rsi")
    def test_rsi_trigger_true(self, mock_rsi, mock_klines_manager):
        mock_klines_manager.get_klines_dataframe.return_value = MagicMock()
        mock_rsi.return_value.iloc.__getitem__.return_value = 20
        trigger = IndicatorTrigger(30, mock_klines_manager)
        assert trigger.rsi_trigger() is True

    @patch("src.utils.triggers.ta.momentum.rsi")
    def test_rsi_trigger_false(self, mock_rsi, mock_klines_manager):
        mock_klines_manager.get_klines_dataframe.return_value = MagicMock()
        mock_rsi.return_value.iloc.__getitem__.return_value = 40
        trigger = IndicatorTrigger(30, mock_klines_manager)
        assert trigger.rsi_trigger() is False


class TestCrossKlinesTrigger:

    @pytest.fixture
    def mock_gatekeeper_storage(self):
        return MagicMock()

    @pytest.fixture
    def mock_journal_manager(self):
        return MagicMock()

    def test_cross_down_to_up_true(self, mock_gatekeeper_storage, mock_journal_manager):
        mock_gatekeeper_storage.get_klines.return_value = [
            [0, 0, 0, 0, 95],
            [0, 0, 0, 0, 105],
        ]
        mock_journal_manager.get.return_value = {"buy_lines": [100], "sell_lines": []}
        trigger = CrossKlinesTrigger(mock_gatekeeper_storage, mock_journal_manager)
        assert trigger.cross_down_to_up() is True

    def test_cross_down_to_up_false(
        self, mock_gatekeeper_storage, mock_journal_manager
    ):
        mock_gatekeeper_storage.get_klines.return_value = [
            [0, 0, 0, 0, 105],
            [0, 0, 0, 0, 110],
        ]
        mock_journal_manager.get.return_value = {"buy_lines": [100], "sell_lines": []}
        trigger = CrossKlinesTrigger(mock_gatekeeper_storage, mock_journal_manager)
        assert trigger.cross_down_to_up() is False

    def test_cross_up_to_down_true(self, mock_gatekeeper_storage, mock_journal_manager):
        mock_gatekeeper_storage.get_klines.return_value = [
            [0, 0, 0, 0, 105],
            [0, 0, 0, 0, 95],
        ]
        mock_journal_manager.get.return_value = {"buy_lines": [], "sell_lines": [100]}
        trigger = CrossKlinesTrigger(mock_gatekeeper_storage, mock_journal_manager)
        assert trigger.cross_up_to_down() is True

    def test_cross_up_to_down_false(
        self, mock_gatekeeper_storage, mock_journal_manager
    ):
        mock_gatekeeper_storage.get_klines.return_value = [
            [0, 0, 0, 0, 95],
            [0, 0, 0, 0, 90],
        ]
        mock_journal_manager.get.return_value = {"buy_lines": [], "sell_lines": [100]}
        trigger = CrossKlinesTrigger(mock_gatekeeper_storage, mock_journal_manager)
        assert trigger.cross_up_to_down() is False


class TestBalanceTrigger:

    @pytest.fixture
    def mock_gatekeeper_storage(self):
        return MagicMock()

    def test_invalid_balance_true(self, mock_gatekeeper_storage):
        mock_gatekeeper_storage.get_balance.return_value = {"USDT": 50}
        trigger = BalanceTrigger(mock_gatekeeper_storage, 100)
        assert trigger.invalid_balance() is True

    def test_invalid_balance_false(self, mock_gatekeeper_storage):
        mock_gatekeeper_storage.get_balance.return_value = {"USDT": 150}
        trigger = BalanceTrigger(mock_gatekeeper_storage, 100)
        assert trigger.invalid_balance() is None
