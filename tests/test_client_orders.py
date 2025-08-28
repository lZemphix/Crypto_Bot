from unittest.mock import patch, MagicMock, mock_open
import json
import pytest
from client.orders import Checkup, Orders
from utils.exceptions import (
    IncorrectOpenOrdersList,
    IncorrectOrdersHistory,
    OrderPlaceException,
)


@patch(
    "builtins.open", new_callable=mock_open, read_data=json.dumps({"symbol": "BTCUSDT"})
)
def test_checkup_get_accuracy(mock_file):
    mock_info = {"result": {"list": [{"lotSizeFilter": {"minOrderQty": "0.0001"}}]}}
    checkup = Checkup()
    checkup.client = MagicMock()
    checkup.client.get_instruments_info.return_value = mock_info
    accuracy = checkup.get_accuracy()
    assert accuracy == 6


def test_orders_get_order_history():
    orders = Orders()
    orders.client = MagicMock()
    orders.client.get_order_history.return_value = {"result": {"list": [1, 2, 3]}}
    history = orders.get_order_history()
    assert history == [1, 2, 3]

    orders.client.get_order_history.side_effect = Exception("Test Error")
    with pytest.raises(IncorrectOrdersHistory):
        orders.get_order_history()


def test_orders_get_open_orders():
    orders = Orders()
    orders.client = MagicMock()
    orders.client.get_open_orders.return_value = {"result": {"list": [4, 5, 6]}}
    open_orders = orders.get_open_orders()
    assert open_orders == [4, 5, 6]

    orders.client.get_open_orders.side_effect = Exception("Test Error")
    with pytest.raises(IncorrectOpenOrdersList):
        orders.get_open_orders()


@patch("client.orders.get_bot_config", return_value=100)
def test_orders_place_buy_order(mock_config):
    orders = Orders()
    orders.client = MagicMock()
    result = orders.place_buy_order()
    assert result is True
    orders.client.place_order.assert_called_once()

    orders.client.place_order.side_effect = Exception("Test Error")
    result = orders.place_buy_order()
    assert result is False


@patch("client.orders.gatekeeper_storage")
@patch.object(Orders, "get_accuracy", return_value=5)
def test_orders_place_sell_order(mock_get_accuracy, mock_storage):
    mock_storage.get_balance.return_value = {"BTC": 0.123456789}
    orders = Orders()
    orders.client = MagicMock()
    orders.symbol = "BTCUSDT"
    result = orders.place_sell_order()
    assert result is True
    orders.client.place_order.assert_called_with(
        category="spot", symbol="BTCUSDT", side="Sell", orderType="Market", qty="0.123"
    )

    orders.client.place_order.side_effect = Exception("Test Error")
    with pytest.raises(OrderPlaceException):
        orders.place_sell_order()


def test_orders_get_avg_order():
    orders = Orders()
    orders.journal = MagicMock()
    orders.journal.get.return_value = {"orders": [90, 100, 110]}
    avg = orders.get_avg_order()
    assert avg == 100.0

    orders.journal.get.return_value = {"orders": []}
    avg = orders.get_avg_order()
    assert avg == 0
