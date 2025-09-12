import pytest
from unittest.mock import MagicMock, patch, mock_open
from src.utils.journal_manager import JournalManager


class TestJournalManager:

    @pytest.fixture
    def mock_journal_manager(self):
        return JournalManager()

    def test_get(self, mock_journal_manager):
        with patch(
            "builtins.open", mock_open(read_data='{"laps": 0, "orders": []}')
        ) as mock_file:
            journal = mock_journal_manager.get()
            assert journal == {"laps": 0, "orders": []}
            mock_file.assert_called_once_with("src/data/trade_journal.json")

    def test_update(self, mock_journal_manager):
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("json.dump") as mock_json_dump:
                data = {"laps": 1, "orders": [1]}
                mock_journal_manager.update(data)
                mock_file.assert_called_once_with("src/data/trade_journal.json", "w")
                mock_json_dump.assert_called_once_with(
                    data, mock_file.return_value, indent=4
                )

    def test_clear(self, mock_journal_manager):
        with patch.object(mock_journal_manager, "update") as mock_update:
            mock_journal_manager.clear()
            mock_update.assert_called_once_with(
                dict(laps=0, orders=[], buy_lines=[], sell_lines=[])
            )
