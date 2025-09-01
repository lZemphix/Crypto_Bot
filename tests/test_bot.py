import pytest
from unittest.mock import MagicMock
from src.data.consts import BOT_STARTED_MESSAGE
from src.scripts.bot import Price, Notifier, States, Bot


class TestPrice:

    @pytest.fixture
    def mock_orders(self):
        return MagicMock()

    @pytest.fixture
    def mock_journal(self):
        return MagicMock()

    @pytest.fixture
    def mock_gatekeeper_storage(self):
        return MagicMock()

    @pytest.fixture
    def mock_telenotify(self):
        return MagicMock()

    @pytest.mark.parametrize(
        "avg_order, klines, expect",
        [
            (12.0, [[0, 0, 0, 0, 10.0], [0, 0, 0, 0, 12.0]], 2.0),
            (12.0, [[0, 0, 0, 0, 12.0], [0, 0, 0, 0, 12.0]], 0),
            (12.0, [[0, 0, 0, 0, 8.0], [0, 0, 0, 0, 12.0]], -2.0),
            (None, [[0, 0, 0, 0, 8.0], [0, 0, 0, 0, 12.0]], TypeError),
            (12.0, None, TypeError),
            (12.0, [], IndexError),
        ],
    )
    def test_get_price_side(
        self, mock_orders, mock_gatekeeper_storage, avg_order, klines, expect
    ):
        mock_orders.get_avg_order.return_value = avg_order
        mock_gatekeeper_storage.get_klines.return_value = klines

        price = Price(mock_orders, mock_gatekeeper_storage)

        if isinstance(expect, type) and issubclass(expect, BaseException):
            with pytest.raises(expect):
                assert price.get_price_side()
        else:
            price.get_price_side() == expect


class TestNotifier:

    @pytest.fixture
    def mock_gatekeeper_storage(self):
        return MagicMock()

    @pytest.fixture
    def mock_telenotify(self):
        return MagicMock()

    @pytest.mark.parametrize(
        "amount_buy, gk_balance, exp",
        [
            (10.0, {"USDT": 12.0, "ETH": 0.1}, True),
            (15.0, {"USDT": 12.0, "ETH": 0.1}, True),
        ],
    )
    def test_send_activate_notify(
        self, mock_gatekeeper_storage, mock_telenotify, amount_buy, gk_balance, exp
    ):
        interval = 5
        symbol = "ETHUSDT"
        coin_name = "ETH"
        usdt_balance = gk_balance["USDT"]
        coin_balance = f"{gk_balance['ETH']:.10f}"
        mock_gatekeeper_storage.get_balance.return_value = gk_balance
        mock_telenotify.bot_status.return_value = 200

        notify = Notifier(
            mock_gatekeeper_storage,
            mock_telenotify,
            interval,
            amount_buy,
            symbol,
            coin_name,
        )
        if isinstance(exp, type) and issubclass(exp, BaseException):
            with pytest.raises(exp):
                assert notify.send_activate_notify()
        else:
            notify.send_activate_notify()
            expected_message = BOT_STARTED_MESSAGE.format(
                symbol=symbol,
                usdt_balance=usdt_balance,
                coin_name=coin_name,
                coin_balance=coin_balance,
                interval=interval,
                amount_buy=amount_buy,
            )
            mock_telenotify.bot_status.assert_called_once_with(expected_message)
