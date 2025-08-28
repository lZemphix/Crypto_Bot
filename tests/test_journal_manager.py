import json
from unittest.mock import patch, mock_open

from utils.journal_manager import JournalManager


def test_journal_manager_get():
    mock_data = {"laps": 5, "orders": [], "buy_lines": [], "sell_lines": []}
    with patch(
        "builtins.open", mock_open(read_data=json.dumps(mock_data))
    ) as mock_file:
        jm = JournalManager()
        journal = jm.get()
        assert journal == mock_data
        mock_file.assert_called_with("src/data/trade_journal.json")


def test_journal_manager_update():
    new_data = {"laps": 6}
    with patch("builtins.open", mock_open()) as mock_file:
        with patch("json.dump") as mock_json_dump:
            jm = JournalManager()
            result = jm.update(new_data)
            assert result is True
            mock_file.assert_called_with("src/data/trade_journal.json", "w")
            mock_json_dump.assert_called_with(
                new_data, mock_file.return_value, indent=4
            )


def test_journal_manager_clear():
    with patch("builtins.open", mock_open()) as mock_file:
        with patch("json.dump") as mock_json_dump:
            jm = JournalManager()
            result = jm.clear()
            assert result is True
            cleared_data = dict(laps=0, orders=[], buy_lines=[], sell_lines=[])
            mock_file.assert_called_with("src/data/trade_journal.json", "w")
            mock_json_dump.assert_called_with(
                cleared_data, mock_file.return_value, indent=4
            )
