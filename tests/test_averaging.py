import pytest
from unittest.mock import MagicMock, patch
from src.scripts.averaging import Averaging, Checkup, Notifier
from utils.exceptions import OrderPlaceException


class TestCheckup:

    @pytest.fixture
    def mock_orders(self):
        return MagicMock()

    @pytest.fixture
    def mock_journal(self):
        return MagicMock()

    @pytest.fixture
    def mock_gatekeeper_storage(self):
        return MagicMock()

    @pytest.mark.parametrize(
        "balance, amount_buy, expect",
        [
            ({"USDT": 12.0}, 10.0, True),  #        balance > ab
            ({"USDT": 10.0}, 12.0, False),  #       balance < ab
            ({"USDT": 12.0}, 12.0, False),  #       balance == ab
            ({"USDT": 12.0}, None, None),  #        ab = None
            ({"USDT": None}, 12.0, None),  #        balance = None
            ({"USDT": "str"}, 12.0, None),  #       balance = str
            (None, 12.0, None),  #                  balance != dict
            ([1, 2, 3], 12.0, None),  #             balance == list
            ({"USDT": 12.0}, [1, 2, 3], None),  #   ab == list
        ],
    )
    def test_valid_balance(
        self,
        mock_gatekeeper_storage,
        mock_orders,
        mock_journal,
        balance,
        amount_buy,
        expect,
    ):
        mock_gatekeeper_storage.get_balance.return_value = balance
        step_buy = 1

        checkup = Checkup(
            mock_gatekeeper_storage,
            mock_orders,
            mock_journal,
            amount_buy,
            step_buy,
        )
        assert checkup.valid_balance() == expect

    @pytest.mark.parametrize(
        "klines, avg_order, expect",
        [
            ([[0, 0, 0, 0, 130]], 150, True),  #    kline < avg_order
            ([[0, 0, 0, 0, 130]], 120, False),  #   kline > avg_order
            ([[0, 0, 0, 0, 130]], 130, False),  #   kline == avg_order
            ([[0, 0, 0, 0, 130]], "str", None),  #  avg_order = str
            ("str", 130, None),  #                  kline = str
            ([], 130, None),  #                     kline = empty list
            ([[0, 0, 0, 0, 130]], None, None),  #   avg_order = str
            (None, 130, None),  #                   kline = None
        ],
    )
    def test_valid_price(
        self,
        mock_orders,
        mock_gatekeeper_storage,
        avg_order,
        klines,
        mock_journal,
        expect,
    ):
        mock_orders.get_avg_order.return_value = avg_order
        mock_gatekeeper_storage.get_klines.return_value = klines
        step_buy = 10.0
        amount_buy = 12.0
        checkup = Checkup(
            mock_gatekeeper_storage,
            mock_orders,
            mock_journal,
            amount_buy,
            step_buy,
        )

        assert checkup.valid_price() == expect

    @pytest.mark.parametrize(
        "last_order, expect",
        [
            (12.0, True),
            (12, True),
            ("12.0", TypeError),
            (None, TypeError),
            ({1: 2}, TypeError),
            ([1, 2, 3], TypeError),
        ],
    )
    def test_update_orders_journal(
        self, mock_gatekeeper_storage, mock_orders, mock_journal, last_order, expect
    ):
        mock_journal.get.return_value = {
            "orders": [10.0, 11.0],
        }
        step_buy = 10.0
        amount_buy = 12.0
        checkup = Checkup(
            mock_gatekeeper_storage,
            mock_orders,
            mock_journal,
            amount_buy,
            step_buy,
        )
        if isinstance(expect, type) and issubclass(expect, BaseException):
            with pytest.raises(expect):
                assert checkup.update_orders_journal(last_order=last_order)
        else:
            assert checkup.update_orders_journal(last_order=last_order) == expect


class TestNotifier:

    @pytest.fixture
    def mock_telenotify(self):
        return MagicMock()

    @pytest.fixture
    def mock_journal(self):
        return MagicMock()

    @pytest.fixture
    def mock_gatekeeper_storage(self):
        return MagicMock()

    # fmt: off
    @pytest.mark.parametrize(
            "balance, last_order, sell_lines, buy_lines, expect",
            [
                ({"USDT": 12.0}, 10.0, [17.0, 22.0], [7.0, 2.0], True), #       Ok
                (None, 10.0, [17.0, 22.0], [7.0, 2.0], AttributeError),#        balance == None
                ([], 10.0, [17.0, 22.0], [7.0, 2.0], AttributeError),#          balance == list
                ({}, 10.0, [17.0, 22.0], [7.0, 2.0], AttributeError),#          balance == empty dict
                ({"USDT": 12.0}, 'str', [17.0, 22.0], [7.0, 2.0], TypeError),#  last_order != float
                ({"USDT": 12.0}, 10.0, 'str', [7.0, 2.0], TypeError),#          sell_lines != list[float]
                ({"USDT": 12.0}, 10.0, [17.0, 22.0], 'str', TypeError),#        buy_lines != list[float]
                ({"12": 12.0}, 10.0, [17.0, 22.0], [7.0, 2.0], KeyError),#      balance not contains USDT
            ]
    )    
    # fmt: on
    def test_send_averaging_notify(
        self,
        last_order,
        mock_gatekeeper_storage,
        mock_journal,
        mock_telenotify,
        expect,
        sell_lines,
        buy_lines,
        balance,
    ):

        mock_gatekeeper_storage.get_balance.return_value = balance
        mock_telenotify.bought.return_value = 200
        mock_journal.get.return_value = {
            "sell_lines": sell_lines,
            "buy_lines": buy_lines,
        }
        notify = Notifier(mock_telenotify, mock_gatekeeper_storage, mock_journal)
        if isinstance(expect, type) and issubclass(expect, BaseException):
            with pytest.raises(expect):
                assert notify.send_averaging_notify(last_order=last_order)
        else:
            notify.send_averaging_notify(last_order=last_order)
            expected_message = f'```\nAverage price: {last_order} USDT\nBalance: {balance["USDT"]}\nSell line: ${sell_lines[0]}\nAverage line: ${buy_lines[0]}```'
            mock_telenotify.bought.assert_called_once()
            mock_telenotify.bought.assert_called_once_with(expected_message)


class TestAveraging:

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

    @pytest.fixture
    def mock_valid_price(self):
        return MagicMock()

    @patch("src.scripts.averaging.time.sleep")
    @pytest.mark.parametrize(
        "valid_balance, cross_down_to_up, valid_price, update_balance, place_buy_order, last_order, expect",
        [
            (True, True, True, True, True, 10.0, True),
        ],
    )
    def test_activate(
        self,
        mock_sleep,
        mock_checkup,
        mock_trigger,
        mock_gatekeeper_storage,
        mock_orders,
        mock_lines,
        mock_metamanager,
        mock_notifier,
        valid_balance,
        valid_price,
        cross_down_to_up,
        place_buy_order,
        update_balance,
        last_order,
        expect,
    ):
        mock_checkup.valid_balance.return_value = valid_balance
        mock_checkup.valid_price.return_value = valid_price
        mock_trigger.cross_down_to_up.return_value = cross_down_to_up
        mock_gatekeeper_storage.update_balance.return_value = update_balance
        mock_orders.place_buy_order.return_value = place_buy_order

        mock_orders.get_order_history.return_value = [{"avgPrice": last_order}]

        averaging = Averaging(
            checkup=mock_checkup,
            trigger=mock_trigger,
            gatekeeper_storage=mock_gatekeeper_storage,
            orders=mock_orders,
            lines=mock_lines,
            metamanager=mock_metamanager,
            notifier=mock_notifier,
        )

        result = averaging.activate()

        assert result == expect

        mock_checkup.valid_balance.assert_called_once()
        mock_checkup.valid_price.assert_called_once()
        mock_trigger.cross_down_to_up.assert_called_once()
        mock_orders.place_buy_order.assert_called_once()
        mock_lines.write_lines.assert_called_once_with(last_order)
        mock_checkup.update_orders_journal.assert_called_once_with(last_order)
        mock_notifier.send_averaging_notify.assert_called_once_with(last_order)
        mock_checkup.update_orders_journal.assert_called_once_with(last_order)
        mock_metamanager.update_all.assert_called_once_with(type="average")
