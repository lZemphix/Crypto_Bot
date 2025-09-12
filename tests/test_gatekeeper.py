import pytest
from unittest.mock import MagicMock, patch
from src.utils.gatekeeper import Formater, GatekeeperStorage, Gatekeeper


class TestFormater:

    def test_format_new_kline(self):
        kline = {
            "topic": "kline.5.spot.ETHUSDT",
            "type": "snapshot",
            "ts": 1622890800000,
            "data": [
                {
                    "timestamp": 1622890800000,
                    "open": 2800.0,
                    "high": 2810.0,
                    "low": 2790.0,
                    "close": 2805.0,
                    "turnover": 1000.0,
                    "confirm": False,
                }
            ],
        }
        formated_kline = Formater.format_new_kline(kline)
        expected_kline = {
            "timestamp": 1622890800000,
            "open": 2800.0,
            "high": 2810.0,
            "low": 2790.0,
            "close": 2805.0,
            "turnover": 1000.0,
            "confirm": False,
        }
        assert formated_kline == expected_kline

    def test_format_balance(self):
        balance = {
            "result": {
                "list": [
                    {
                        "coin": [
                            {"coin": "USDT", "walletBalance": "1000.0"},
                            {"coin": "ETH", "walletBalance": "10.0"},
                        ]
                    }
                ]
            }
        }
        formated_balance = Formater.format_balance(balance)
        expected_balance = {"USDT": 1000.0, "ETH": 10.0}
        assert formated_balance == expected_balance


class TestGatekeeperStorage:

    @pytest.fixture
    def mock_klines(self):
        return MagicMock()

    @pytest.fixture
    def mock_client(self):
        return MagicMock()

    def test_get(self, mock_klines, mock_client):
        storage = GatekeeperStorage(mock_klines, mock_client, "UNIFIED")
        assert storage.get() == {"balance": {}, "klines": []}

    def test_update(self, mock_klines, mock_client):
        storage = GatekeeperStorage(mock_klines, mock_client, "UNIFIED")
        storage.update("balance", {"USDT": 1000.0})
        assert storage.get_balance() == {"USDT": 1000.0}

    def test_update_balance(self, mock_klines, mock_client):
        storage = GatekeeperStorage(mock_klines, mock_client, "UNIFIED")
        mock_client.get_wallet_balance.return_value = {
            "result": {
                "list": [
                    {
                        "coin": [
                            {"coin": "USDT", "walletBalance": "1000.0"},
                            {"coin": "ETH", "walletBalance": "10.0"},
                        ]
                    }
                ]
            }
        }
        storage.update_balance()
        assert storage.get_balance() == {"USDT": 1000.0, "ETH": 10.0}

    def test_update_klines(self, mock_klines, mock_client):
        storage = GatekeeperStorage(mock_klines, mock_client, "UNIFIED")
        mock_klines.get_klines.return_value = [
            [8, 9, 10, 11, 12, 13, 14],
            [1, 2, 3, 4, 5, 6, 7],
        ]
        storage.update_klines()
        assert storage.get_klines() == [
            [1, 2, 3, 4, 5, 6, 7],
            [8, 9, 10, 11, 12, 13, 14],
        ]


class TestGatekeeper:

    @pytest.fixture
    def mock_gatekeeper_storage(self):
        return MagicMock()

    @patch("src.utils.gatekeeper.WebSocket")
    def test_klines_callback(self, mock_websocket, mock_gatekeeper_storage):
        gatekeeper = Gatekeeper(mock_gatekeeper_storage, "ETHUSDT", 5)
        kline = {
            "topic": "kline.5.spot.ETHUSDT",
            "type": "snapshot",
            "ts": 1622890800000,
            "data": [
                {
                    "timestamp": 1622890800000,
                    "open": 2800.0,
                    "high": 2810.0,
                    "low": 2790.0,
                    "close": 2805.0,
                    "turnover": 1000.0,
                    "confirm": False,
                }
            ],
        }
        mock_gatekeeper_storage.get.return_value = {
            "balance": {"USDT": 1000.0},
            "klines": [[1, 2, 3, 4, 5, 6, 7]],
        }
        gatekeeper.klines_callback(kline)
        mock_gatekeeper_storage.update.assert_called_once_with(
            "klines", [list(Formater.format_new_kline(kline).values())[:-1]]
        )
