from unittest.mock import patch, MagicMock
import pandas as pd
from utils.triggers import IndicatorTrigger, CrossKlinesTrigger, BalanceTrigger


@patch("utils.triggers.ta.momentum.rsi")
@patch("utils.triggers.KlinesManager")
def test_indicator_trigger_rsi_trigger(mock_klines_manager, mock_rsi):
    # Case 1: RSI <= self.RSI
    mock_df = pd.DataFrame({"close": [1, 2, 3]})
    mock_klines_manager.return_value.get_klines_dataframe.return_value = mock_df
    mock_rsi.return_value = pd.Series([20])
    trigger = IndicatorTrigger()
    trigger.RSI = 30
    assert trigger.rsi_trigger()

    # Case 2: RSI > self.RSI
    mock_rsi.return_value = pd.Series([40])
    assert not trigger.rsi_trigger()

    # Case 3: ValueError
    mock_klines_manager.return_value.get_klines_dataframe.side_effect = ValueError
    assert not trigger.rsi_trigger()


@patch("utils.triggers.gatekeeper_storage")
def test_cross_klines_trigger_get_klines(mock_gatekeeper):
    mock_gatekeeper.get_klines.return_value = [[1, 2, 3, 4, "100"], [1, 2, 3, 4, "110"]]
    trigger = CrossKlinesTrigger()
    current, prev = trigger.get_klines()
    assert current == 110.0
    assert prev == 100.0


def test_cross_klines_trigger_get_lines():
    trigger = CrossKlinesTrigger()
    trigger.journal = MagicMock()
    trigger.journal.get.return_value = {"buy_lines": [90, 80], "sell_lines": [110, 120]}
    buy_lines, sell_lines = trigger.get_lines()
    assert buy_lines == [90, 80]
    assert sell_lines == [110, 120]


def test_cross_klines_trigger_cross_down_to_up():
    trigger = CrossKlinesTrigger()
    trigger.get_klines = MagicMock(return_value=(105.0, 95.0))  # current, prev
    trigger.get_lines = MagicMock(return_value=([100, 90], [110, 120]))  # buy, sell
    assert trigger.cross_down_to_up() is True

    trigger.get_klines = MagicMock(return_value=(100.0, 95.0))
    assert trigger.cross_down_to_up() is True

    trigger.get_klines = MagicMock(return_value=(98.0, 95.0))
    assert trigger.cross_down_to_up() is False


def test_cross_klines_trigger_cross_up_to_down():
    trigger = CrossKlinesTrigger()
    trigger.get_klines = MagicMock(return_value=(105.0, 115.0))  # current, prev
    trigger.get_lines = MagicMock(return_value=([100, 90], [110, 120]))  # buy, sell
    assert trigger.cross_up_to_down() is True

    trigger.get_klines = MagicMock(return_value=(110.0, 115.0))
    assert trigger.cross_up_to_down() is True

    trigger.get_klines = MagicMock(return_value=(112.0, 115.0))
    assert trigger.cross_up_to_down() is False


@patch("utils.triggers.gatekeeper_storage")
def test_balance_trigger_invalid_balance(mock_gatekeeper):
    trigger = BalanceTrigger()
    trigger.amount_buy = 100

    # Case 1: balance < amount_buy
    mock_gatekeeper.get_balance.return_value = {"USDT": 50}
    assert trigger.invalid_balance() is True

    # Case 2: balance >= amount_buy
    mock_gatekeeper.get_balance.return_value = {"USDT": 150}
    assert trigger.invalid_balance() is None
