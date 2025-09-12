import pytest
from unittest.mock import MagicMock, patch, mock_open
from src.utils.metadata_manager import MetaManager, MetaPreviousTypes
import datetime


class TestMetaManager:

    @pytest.fixture
    def mock_journal_manager(self):
        return MagicMock()

    @pytest.fixture
    def mock_metadata_manager(self, mock_journal_manager):
        return MetaManager(mock_journal_manager)

    def test_get(self, mock_metadata_manager):
        with patch(
            "builtins.open",
            mock_open(read_data='{"actual": {}, "previous_actions": {}}'),
        ) as mock_file:
            metadata = mock_metadata_manager.get()
            assert metadata == {"actual": {}, "previous_actions": {}}
            mock_file.assert_called_once_with("metadata.json")

    def test_update(self, mock_metadata_manager):
        with patch("builtins.open", mock_open(read_data="{}")) as mock_file:
            with patch("json.dump") as mock_json_dump:
                with patch.object(mock_metadata_manager, "get") as mock_get:
                    mock_get.return_value = {"actual": {}}
                    mock_metadata_manager.update("actual", {"orders_amount": 1})
                    mock_file.assert_called_with("metadata.json", "w")
                    mock_json_dump.assert_called_once_with(
                        {"actual": {"orders_amount": 1}},
                        mock_file.return_value,
                        indent=4,
                    )

    def test_update_last_action(self, mock_metadata_manager):
        with patch.object(mock_metadata_manager, "update") as mock_update:
            mock_metadata_manager.update_last_action("buy")
            assert mock_update.call_count == 1

    def test_update_actual(self, mock_metadata_manager, mock_journal_manager):
        with patch.object(mock_metadata_manager, "update") as mock_update:
            mock_journal_manager.get.return_value = {
                "orders": [100, 120],
                "sell_lines": [130, 140],
                "buy_lines": [90, 80],
            }
            mock_metadata_manager.update_actual()
            mock_update.assert_called_once_with(
                "actual",
                {
                    "orders_amount": 2,
                    "avg_order_price": 110.0,
                    "closest_s_line": 130,
                    "closest_a_line": 90,
                },
            )

    def test_update_previous_actions(self, mock_metadata_manager):
        with patch(
            "builtins.open",
            mock_open(read_data='{"previous_actions": {"buy_actions": []}}'),
        ) as mock_file:
            with patch("json.dump") as mock_json_dump:
                with patch.object(mock_metadata_manager, "get") as mock_get:
                    mock_get.return_value = {"previous_actions": {"buy_actions": []}}
                    mock_metadata_manager.update_previous_actions(
                        MetaPreviousTypes.BUY_ACTION, 100
                    )
                    mock_file.assert_called_with("metadata.json", "w")
                    mock_json_dump.assert_called_once_with(
                        {"previous_actions": {"buy_actions": [100]}},
                        mock_file.return_value,
                        indent=4,
                    )

    def test_update_all(self, mock_metadata_manager):
        with patch.object(
            mock_metadata_manager, "update_previous_actions"
        ) as mock_update_previous_actions:
            with patch.object(
                mock_metadata_manager, "update_last_action"
            ) as mock_update_last_action:
                with patch.object(
                    mock_metadata_manager, "update_actual"
                ) as mock_update_actual:
                    mock_metadata_manager.update_all("buy", 100)
                    mock_update_previous_actions.assert_called_once_with(
                        MetaPreviousTypes.BUY_ACTION, 100
                    )
                    mock_update_last_action.assert_called_once_with(type="buy")
                    mock_update_actual.assert_called_once()
