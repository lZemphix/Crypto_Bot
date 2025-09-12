import pytest
from unittest.mock import MagicMock, patch
from src.utils.lines_manager import LinesManager


class TestLinesManager:

    @pytest.fixture
    def mock_journal_manager(self):
        return MagicMock()

    @patch("src.utils.lines_manager.get_bot_config")
    def test_create_lines_no_orders(self, mock_get_bot_config, mock_journal_manager):
        lines_manager = LinesManager(mock_journal_manager)
        mock_journal_manager.get.return_value = {"orders": []}
        mock_get_bot_config.side_effect = [0.1, 0.2]  # step_buy, step_sell

        sell_lines, buy_lines = lines_manager.create_lines(100.0)

        assert len(sell_lines) == 30
        assert len(buy_lines) == 30
        assert sell_lines[0] == 100.2
        assert buy_lines[0] == 99.9

    @patch("src.utils.lines_manager.get_bot_config")
    def test_create_lines_with_orders(self, mock_get_bot_config, mock_journal_manager):
        lines_manager = LinesManager(mock_journal_manager)
        mock_journal_manager.get.return_value = {"orders": [90.0, 110.0]}
        mock_get_bot_config.side_effect = [0.1, 0.2]  # step_buy, step_sell

        sell_lines, buy_lines = lines_manager.create_lines(100.0)

        assert len(sell_lines) == 30
        assert len(buy_lines) == 30
        assert sell_lines[0] == 100.2
        assert buy_lines[0] == 99.9

    def test_write_lines(self, mock_journal_manager):
        lines_manager = LinesManager(mock_journal_manager)
        mock_journal_manager.get.return_value = {"orders": []}
        with patch.object(lines_manager, "create_lines") as mock_create_lines:
            mock_create_lines.return_value = ([1, 2, 3], [4, 5, 6])
            lines_manager.write_lines(100.0)
            mock_journal_manager.update.assert_called_once_with(
                {"orders": [], "sell_lines": [1, 2, 3], "buy_lines": [4, 5, 6]}
            )
