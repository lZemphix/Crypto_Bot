import pytest
from unittest.mock import MagicMock, patch
from src.data.consts import BOT_STARTED_MESSAGE
from src.scripts.bot import Price, Notifier, States, Bot
from utils.states import BotState


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


class TestStates:

    @pytest.fixture
    def mock_gatekeeper_storage(self):
        return MagicMock()

    @pytest.fixture
    def mock_balance_trigger(self):
        return MagicMock()

    @pytest.fixture
    def mock_first_buy(self):
        return MagicMock()

    @pytest.fixture
    def mock_averaging(self):
        return MagicMock()

    @pytest.fixture
    def mock_sell(self):
        return MagicMock()

    @pytest.fixture
    def mock_notifier(self):
        return MagicMock()

    @pytest.fixture
    def mock_journal(self):
        return MagicMock()

    @pytest.fixture
    def mock_price(self):
        return MagicMock()

    @patch("src.scripts.bot.time.sleep", return_value=None)
    def test_insufficient_balance_state_sell_activates(
        self,
        mock_sleep,
        mock_balance_trigger,
        mock_first_buy,
        mock_averaging,
        mock_sell,
        mock_notifier,
        mock_journal,
        mock_price,
        mock_gatekeeper_storage,
    ):

        states = States(
            mock_balance_trigger,
            mock_first_buy,
            mock_averaging,
            mock_sell,
            mock_notifier,
            mock_journal,
            mock_price,
            mock_gatekeeper_storage,
        )
        mock_balance_trigger.invalid_balance.side_effect = [True, True, False]
        mock_sell.activate.return_value = True
        result = states.insufficient_balance_state()
        assert result.value == BotState.FIRST_BUY.value
        mock_notifier.send_nem_notify.assert_called_once()
        assert mock_sell.activate.call_count == 1

    @pytest.mark.parametrize(
        "orders, price_side, exp",
        [
            ([], None, BotState.FIRST_BUY),
            ([10.0, 12.0], 1, BotState.SELL),
            ([10.0, 12.0], 0, BotState.AVERAGING),
        ],
    )
    def test_waiting_state(
        self,
        orders,
        price_side,
        mock_journal,
        mock_price,
        mock_averaging,
        mock_balance_trigger,
        mock_first_buy,
        mock_sell,
        mock_notifier,
        mock_gatekeeper_storage,
        exp,
    ):
        states = States(
            mock_balance_trigger,
            mock_first_buy,
            mock_averaging,
            mock_sell,
            mock_notifier,
            mock_journal,
            mock_price,
            mock_gatekeeper_storage,
        )
        mock_journal.get.return_value = {"orders": orders}
        mock_price.get_price_side.return_value = price_side
        result = states.waiting_state()
        assert result.value == exp.value

    @pytest.mark.parametrize("activate_result", [True, False])
    def test_averaging_state(
        self,
        mock_averaging,
        mock_gatekeeper_storage,
        mock_balance_trigger,
        mock_first_buy,
        mock_sell,
        mock_notifier,
        mock_journal,
        mock_price,
        activate_result,
    ):
        states = States(
            mock_balance_trigger,
            mock_first_buy,
            mock_averaging,
            mock_sell,
            mock_notifier,
            mock_journal,
            mock_price,
            mock_gatekeeper_storage,
        )
        mock_averaging.activate.return_value = activate_result
        result = states.averaging_state()
        assert result.value == BotState.WAITING.value
        if activate_result:
            mock_gatekeeper_storage.update_balance.assert_called_once()
        else:
            mock_gatekeeper_storage.update_balance.assert_not_called()

    @pytest.mark.parametrize(
        "activate_result, exp",
        [
            (True, BotState.FIRST_BUY),
            (False, BotState.WAITING),
        ],
    )
    def test_sell_state(
        self,
        mock_averaging,
        mock_gatekeeper_storage,
        mock_balance_trigger,
        mock_first_buy,
        mock_sell,
        mock_notifier,
        mock_journal,
        mock_price,
        activate_result,
        exp,
    ):
        states = States(
            mock_balance_trigger,
            mock_first_buy,
            mock_averaging,
            mock_sell,
            mock_notifier,
            mock_journal,
            mock_price,
            mock_gatekeeper_storage,
        )
        mock_sell.activate.return_value = activate_result
        result = states.sell_state()
        assert result.value == exp.value
        if activate_result:
            mock_gatekeeper_storage.update_balance.assert_called_once()
        else:
            mock_gatekeeper_storage.update_balance.assert_not_called()

    @pytest.mark.parametrize(
        "activate_result, exp",
        [
            (True, BotState.WAITING),
            (False, BotState.FIRST_BUY),
        ],
    )
    def test_first_buy_state(
        self,
        mock_averaging,
        mock_gatekeeper_storage,
        mock_balance_trigger,
        mock_first_buy,
        mock_sell,
        mock_notifier,
        mock_journal,
        mock_price,
        activate_result,
        exp,
    ):
        mock_first_buy.activate.return_value = activate_result
        states = States(
            mock_balance_trigger,
            mock_first_buy,
            mock_averaging,
            mock_sell,
            mock_notifier,
            mock_journal,
            mock_price,
            mock_gatekeeper_storage,
        )
        result = states.first_buy_state()
        assert result.value == exp.value
        if activate_result:
            mock_gatekeeper_storage.update_balance.assert_called_once()
        else:
            mock_gatekeeper_storage.update_balance.assert_not_called()
