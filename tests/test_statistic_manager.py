from unittest.mock import patch, MagicMock
import datetime
from utils.statistic_manager import DateManager, StatisticManager


@patch("utils.statistic_manager.StatisticTable")
def test_date_manager_date_delta_no_stats(mock_stats_table):
    mock_stats_table.return_value.get_all_statistic.return_value = []
    dm = DateManager()
    assert dm.date_delta() is True


@patch("utils.statistic_manager.StatisticTable")
@patch("utils.statistic_manager.datetime")
def test_date_manager_date_delta_older_than_day(mock_datetime, mock_stats_table):
    last_stat = MagicMock()
    last_stat.date = datetime.datetime(2023, 1, 1)
    mock_stats_table.return_value.get_all_statistic.return_value = [last_stat]
    mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 3)
    mock_datetime.timedelta = datetime.timedelta
    dm = DateManager()
    assert dm.date_delta() is True


@patch("utils.statistic_manager.StatisticTable")
@patch("utils.statistic_manager.datetime")
def test_date_manager_date_delta_within_day(mock_datetime, mock_stats_table):
    last_stat = MagicMock()
    last_stat.date = datetime.datetime(2023, 1, 1, 12, 0, 0)
    mock_stats_table.return_value.get_all_statistic.return_value = [last_stat]
    mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 18, 0, 0)
    mock_datetime.timedelta = datetime.timedelta
    dm = DateManager()
    assert dm.date_delta() is False


@patch("utils.statistic_manager.StatisticTable")
@patch.object(DateManager, "date_delta", return_value=True)
def test_statistic_manager_add_statistic_true(mock_date_delta, mock_stats_table):
    sm = StatisticManager()
    sm.add_statistic(1000.0, 5, 50.0)
    mock_stats_table.return_value.add_statistic.assert_called_once_with(
        balance=1000.0, actions=5, profit=50.0
    )


@patch("utils.statistic_manager.StatisticTable")
@patch.object(DateManager, "date_delta", return_value=False)
def test_statistic_manager_add_statistic_false(mock_date_delta, mock_stats_table):
    sm = StatisticManager()
    sm.add_statistic(1000.0, 5, 50.0)
    mock_stats_table.return_value.add_statistic.assert_not_called()
