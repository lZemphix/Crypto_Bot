import pytest
from unittest.mock import MagicMock, patch
from src.scripts.sell import Sell, Checkup, Notifier
from utils.exceptions import OrderPlaceException


class TestCheckup:

    @pytest.fixture
    def mock_orders(self):
        return MagicMock()

    @pytest.fixture
    def mock_gatekeeper_storage(self):
        return MagicMock()

    @pytest.mark.parametrize(
        "klines, avg_order, expect",
        [
            ([[0, 0, 0, 0, 130]], 120, True),  #    kline < avg_order
            ([[0, 0, 0, 0, 130]], 130, False),  #   kline == avg_order
            ([[0, 0, 0, 0, 130]], "str", TypeError),  #  avg_order = str
            ("string", 130, IndexError),  #                  kline = str
            ([], 130, IndexError),  #                     kline = empty list
            ([[0, 0, 0, 0, 130]], None, TypeError),  #   avg_order = str
            (None, 130, TypeError),  #                   kline = None
        ],
    )
    def test_valid_price(
        self,
        mock_orders,
        mock_gatekeeper_storage,
        avg_order,
        klines,
        expect,
    ):
        mock_orders.get_avg_order.return_value = avg_order
        mock_gatekeeper_storage.get_klines.return_value = klines

        step_sell = 10

        checkup = Checkup(mock_gatekeeper_storage, mock_orders, step_sell)

        if isinstance(expect, type) and issubclass(expect, BaseException):
            with pytest.raises(expect):
                assert checkup.valid_price() == expect
        else:
            assert checkup.valid_price() == expect

    def valid_price(self):
        actual_price = float(self.gatekeeper_storage.get_klines()[-1][4])
        sell_price = self.orders.get_avg_order() + self.step_sell
        return actual_price >= sell_price


class TestNotifier:

    @pytest.fixture
    def mock_telenotify(self):
        return MagicMock()

    @pytest.fixture
    def mock_gatekeeper_storage(self):
        return MagicMock()

    @pytest.fixture
    def mock_orders(self):
        return MagicMock()

    # fmt: off
    @pytest.mark.parametrize(
            "balance, last_order, expect",
            [
                ({"USDT": 12.0}, 10.0, True), #       Ok
                (None, 10.0, AttributeError),#        balance == None
                ([], 10.0, AttributeError),#          balance == list
                ({}, 10.0, AttributeError),#          balance == empty dict
                ({"USDT": 12.0}, None, TypeError),#  last_order == None
                ({"12": 12.0}, 10.0,  KeyError),#      balance not contains USDT
            ]
    )    
    # fmt: on
    def test_send_sell_notify(
        self,
        last_order,
        mock_telenotify,
        mock_orders,
        mock_gatekeeper_storage,
        expect,
        balance,
    ):
        coin_qty = 0.1
        coin_name = "ETH"
        mock_orders.get_order_history.return_value = [
            {"avgPrice": last_order, "cumExecQty": coin_qty}
        ]
        mock_telenotify.bought.return_value = 200
        mock_gatekeeper_storage.get_balance.return_value = balance
        notify = Notifier(
            mock_telenotify, coin_name, mock_gatekeeper_storage, mock_orders
        )
        if isinstance(expect, type) and issubclass(expect, BaseException):
            with pytest.raises(expect):
                assert notify.send_sell_notify()
        else:
            notify.send_sell_notify()
            expected_message = f"Bot was sold```\n{coin_qty:.10f} {coin_name} for {last_order}.\nTotal: price: {coin_qty*last_order}\nBalance: {balance}```"
            mock_telenotify.sold.assert_called_once_with(expected_message)


class TestSell:

    @pytest.fixture
    def mock_lines(self):
        return MagicMock()

    @pytest.fixture
    def mock_gatekeeper_storage(self):
        return MagicMock()

    @pytest.fixture
    def mock_checkup(self):
        return MagicMock()

    @pytest.fixture
    def mock_trigger(self):
        return MagicMock()

    @pytest.fixture
    def mock_orders(self):
        return MagicMock()

    @pytest.fixture
    def mock_notifier(self):
        return MagicMock()

    @pytest.fixture
    def mock_metamanager(self):
        return MagicMock()
