
from unittest.mock import patch, MagicMock
from utils.gatekeeper import Formater, GatekeeperStorage, Gatekeeper


def test_formater_format_new_kline():
    raw_kline = {
        "data": [
            {
                "timestamp": 1672531200000,
                "open": "100",
                "high": "110",
                "low": "90",
                "close": "105",
                "turnover": "105000",
                "confirm": True,
                "extra": "data"
            }
        ]
    }
    formated = Formater.format_new_kline(raw_kline)
    expected = {
        "timestamp": 1672531200000,
        "open": "100",
        "high": "110",
        "low": "90",
        "close": "105",
        "turnover": "105000",
        "confirm": True
    }
    assert formated == expected


def test_formater_format_balance():
    raw_balance = {
        "result": {
            "list": [
                {
                    "coin": [
                        {"coin": "USDT", "walletBalance": "1000.0"},
                        {"coin": "BTC", "walletBalance": "0.5"}
                    ]
                }
            ]
        }
    }
    formated = Formater.format_balance(raw_balance)
    expected = {"USDT": 1000.0, "BTC": 0.5}
    assert formated == expected


def test_gatekeeper_storage():
    storage = GatekeeperStorage()
    assert storage.get() == {"balance": {}, "klines": []}
    storage.update("balance", {"USDT": 100})
    assert storage.get_balance() == {"USDT": 100}
    storage.update("klines", [1, 2, 3])
    assert storage.get_klines() == [1, 2, 3]


@patch('utils.gatekeeper.get_klines')
@patch.object(GatekeeperStorage, 'update')
def test_gatekeeper_storage_req_update_klines(mock_update, mock_get_klines):
    mock_get_klines.get_klines.return_value = [3, 2, 1]
    storage = GatekeeperStorage()
    storage._GatekeeperStorage__req_update("klines")
    mock_update.assert_called_once_with("klines", [1, 2, 3])


@patch.object(GatekeeperStorage, 'update')
def test_gatekeeper_storage_req_update_balance(mock_update):
    storage = GatekeeperStorage()
    storage.client = MagicMock()
    storage.client.get_wallet_balance.return_value = "raw_balance"
    with patch('utils.gatekeeper.Formater.format_balance', return_value={"USDT": 120}) as mock_format:
        storage._GatekeeperStorage__req_update("balance")
        mock_format.assert_called_once_with("raw_balance")
        mock_update.assert_called_once_with("balance", {"USDT": 120})


@patch.object(GatekeeperStorage, '_GatekeeperStorage__req_update')
def test_gatekeeper_storage_update_methods(mock_req_update):
    storage = GatekeeperStorage()
    storage.update_balance()
    mock_req_update.assert_called_with("balance")
    storage.update_klines()
    mock_req_update.assert_called_with("klines")


@patch('utils.gatekeeper.gatekeeper_storage')
@patch('utils.gatekeeper.Formater')
@patch('utils.gatekeeper.WebSocket')
def test_gatekeeper_klines_callback(mock_ws, mock_formater, mock_storage):
    gatekeeper = Gatekeeper()
    mock_formater_instance = mock_formater.return_value

    # Case 1: new kline is confirmed
    mock_formater_instance.format_new_kline.return_value = {"confirm": True}
    gatekeeper.klines_callback({"data": [{}]})
    mock_storage.update_klines.assert_called_once()

    # Case 2: storage klines are empty
    mock_storage.get.return_value = {"klines": []}
    mock_formater_instance.format_new_kline.return_value = {"confirm": False}
    gatekeeper.klines_callback({"data": [{}]})
    mock_storage.update_klines.assert_called_with()

    # Case 3: storage balance is empty
    mock_storage.get.return_value = {"klines": [1], "balance": {}}
    gatekeeper.klines_callback({"data": [{}]})
    mock_storage.update_balance.assert_called_once()

    # Case 4: update last kline
    mock_storage.get.return_value = {"klines": [[1], [2]], "balance": {"USDT": 100}}
    mock_formater_instance.format_new_kline.return_value = {"c": 3, "confirm": False}
    gatekeeper.klines_callback({"data": [{}]})
    mock_storage.update.assert_called_once()
