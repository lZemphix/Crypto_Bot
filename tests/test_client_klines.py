
from unittest.mock import MagicMock
from client.klines import Klines


def test_klines_get_klines_success():
    klines = Klines()
    klines.client = MagicMock()
    mock_response = {
        "result": {
            "list": [1, 2, 3]
        }
    }
    klines.client.get_kline.return_value = mock_response
    result = klines.get_klines()
    assert result == [1, 2, 3]
    klines.client.get_kline.assert_called_once_with(
        symbol=klines.symbol,
        interval=klines.interval,
        limit=200,
        category="spot",
    )


def test_klines_get_klines_exception():
    klines = Klines()
    klines.client = MagicMock()
    klines.client.get_kline.side_effect = Exception("Test Error")
    result = klines.get_klines()
    assert result is None
