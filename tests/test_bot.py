import pytest
from unittest.mock import MagicMock
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
