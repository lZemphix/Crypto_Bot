import json
from unittest.mock import patch, mock_open, MagicMock
import datetime
from utils.metadata_manager import MetaManager


@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"test": "data"}))
def test_meta_manager_get(mock_file):
    mm = MetaManager()
    data = mm.get()
    assert data == {"test": "data"}
    mock_file.assert_called_with("metadata.json")


@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
def test_meta_manager_update(mock_json_dump, mock_file):
    with patch.object(
        MetaManager, "get", return_value={"target": "old_data"}
    ) as mock_get:
        mm = MetaManager()
        mm.update("target", "new_data")
        mock_get.assert_called_once()
        mock_file.assert_called_with("metadata.json", "w")
        mock_json_dump.assert_called_with({"target": "new_data"}, mock_file(), indent=4)


@patch.object(MetaManager, "update")
@patch("datetime.datetime")
def test_meta_manager_update_last_action(mock_dt, mock_update):
    fake_now = datetime.datetime(2023, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    mock_dt.now.return_value = fake_now
    mock_dt.strftime.return_value = "2023-01-01 12:00:00"

    mm = MetaManager()
    mm.update_last_action("BUY")

    expected_data = {
        "type": "BUY",
        "date": "2023-01-01 12:00:00",
    }
    mock_update.assert_called_once_with("last_action", expected_data)


@patch("utils.metadata_manager.JournalManager")
@patch.object(MetaManager, "update")
def test_meta_manager_update_actual(mock_update, mock_jm):
    mock_journal_instance = MagicMock()
    mock_journal_instance.get.return_value = {
        "orders": [90, 110],
        "sell_lines": [120, 130],
        "buy_lines": [80, 70],
    }
    mock_jm.return_value = mock_journal_instance

    mm = MetaManager()
    mm.update_actual()

    expected_data = {
        "orders_amount": 2,
        "avg_order_price": 100.0,
        "closest_s_line": 120,
        "closest_a_line": 80,
    }
    mock_update.assert_called_once_with("actual", expected_data)


@patch.object(MetaManager, "update_last_action")
@patch.object(MetaManager, "update_actual")
def test_meta_manager_update_all(mock_update_actual, mock_update_last_action):
    mm = MetaManager()
    mm.update_all("SELL")
    mock_update_last_action.assert_called_once_with(type="SELL")
    mock_update_actual.assert_called_once()
