
from unittest.mock import patch, MagicMock
from utils.lines_manager import LinesManager


@patch('utils.lines_manager.get_bot_config')
@patch('utils.lines_manager.JournalManager')
def test_lines_manager_create_lines_no_orders(mock_jm, mock_config):
    mock_journal_instance = MagicMock()
    mock_jm.return_value = mock_journal_instance
    mock_journal_instance.get.return_value = {"orders": []}
    mock_config.side_effect = lambda key: 0.5 if key == 'stepBuy' else 0.6

    lm = LinesManager()
    sell_lines, buy_lines = lm.create_lines(100.0)

    assert len(sell_lines) == 30
    assert len(buy_lines) == 30
    assert sell_lines[0] == round(100.0 + 0.6 * 1, 3)
    assert buy_lines[0] == round(100.0 - 0.5 * 1, 3)


@patch('utils.lines_manager.get_bot_config')
@patch('utils.lines_manager.JournalManager')
def test_lines_manager_create_lines_with_orders(mock_jm, mock_config):
    mock_journal_instance = MagicMock()
    mock_jm.return_value = mock_journal_instance
    mock_journal_instance.get.return_value = {"orders": [90, 110]}
    mock_config.side_effect = lambda key: 0.5 if key == 'stepBuy' else 0.6

    lm = LinesManager()
    sell_lines, buy_lines = lm.create_lines(100.0)

    avg_order = sum([90, 110]) / 2
    assert len(sell_lines) == 30
    assert len(buy_lines) == 30
    assert sell_lines[0] == round(avg_order + 0.6 * 1, 3)
    assert buy_lines[0] == round(100.0 - 0.5 * 1, 3)


@patch('utils.lines_manager.JournalManager')
def test_lines_manager_write_lines(mock_jm):
    mock_journal_instance = MagicMock()
    mock_jm.return_value = mock_journal_instance
    mock_journal_instance.get.return_value = {"orders": [], "sell_lines": [], "buy_lines": []}

    lm = LinesManager()
    # Mocking create_lines to isolate write_lines functionality
    lm.create_lines = MagicMock(return_value=([1, 2], [3, 4]))

    result = lm.write_lines(100.0)

    assert result is True
    mock_journal_instance.get.assert_called_once()
    lm.create_lines.assert_called_once_with(100.0)
    expected_data = {"orders": [], "sell_lines": [1, 2], "buy_lines": [3, 4]}
    mock_journal_instance.update.assert_called_once_with(expected_data)
