import pytest
from unittest.mock import MagicMock, patch
from data.consts import FIRST_BUY_MESSAGE
from src.scripts.first_buy import FirstBuy, Checkup, Notifier


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

    @pytest.fixture
    def mock_telenotify(self):
        return MagicMock()

    @pytest.mark.parametrize(
        "balance, amount_buy, expect",
        [
            ({"USDT": 12.0}, 10.0, True),  #            balance > ab
            ({"USDT": 10.0}, 12.0, False),  #           balance < ab
            ({"USDT": 12.0}, 12.0, False),  #           balance == ab
            ({"USDT": 12.0}, None, TypeError),  #       ab = None
            ({"USDT": None}, 12.0, TypeError),  #       balance = None
            ({"USDT": "str"}, 12.0, TypeError),  #      balance = str
            (None, 12.0, TypeError),  #                 balance != dict
            ([1, 2, 3], 12.0, TypeError),  #            balance == list
            ({"USDT": 12.0}, [1, 2, 3], TypeError),  #  ab == list
            ({"12": 12.0}, 12.0, KeyError),  #          balance not contains USDT
        ],
    )
    def test_valid_balance(
        self,
        mock_gatekeeper_storage,
        mock_telenotify,
        mock_journal,
        balance,
        amount_buy,
        expect,
    ):
        mock_gatekeeper_storage.get_balance.return_value = balance

        checkup = Checkup(
            mock_gatekeeper_storage,
            mock_journal,
            mock_telenotify,
            amount_buy,
        )

        if isinstance(expect, type) and issubclass(expect, BaseException):
            with pytest.raises(expect):
                assert checkup.valid_balance()
        else:
            assert checkup.valid_balance() == expect

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
        self, mock_gatekeeper_storage, mock_telenotify, mock_journal, last_order, expect
    ):
        mock_journal.get.return_value = {
            "orders": [10.0, 11.0],
        }
        checkup = Checkup(
            mock_gatekeeper_storage,
            mock_journal,
            mock_telenotify,
            1.0,
        )
        if isinstance(expect, type) and issubclass(expect, BaseException):
            with pytest.raises(expect):
                assert checkup.update_orders_journal(last_order=last_order)
        else:
            checkup.update_orders_journal(last_order=last_order)
            expected_message = {
                "orders": [10.0, 11.0, last_order],
            }
            mock_journal.get.assert_called_once()
            mock_journal.update.assert_called_once_with(expected_message)


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
    def test_send_buy_notify(
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
                assert notify.send_buy_notify(last_order=last_order)
        else:
            notify.send_buy_notify(last_order=last_order)
            expected_message = FIRST_BUY_MESSAGE.format(
                buy_price=last_order,
                balance=balance["USDT"],
                sell_line=sell_lines[0],
                buy_line=buy_lines[0],
            )
            mock_telenotify.bought.assert_called_once()
            mock_telenotify.bought.assert_called_once_with(expected_message)


class TestFirstBuy:

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

    @patch("src.scripts.first_buy.time.sleep")
    @pytest.mark.parametrize(
        "valid_balance, rsi_trigger, write_lines, place_buy_order, last_order, expect",
        [
            (True, True, True, True, 10.0, True),
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
        rsi_trigger,
        place_buy_order,
        last_order,
        write_lines,
        expect,
    ):
        mock_checkup.valid_balance.return_value = valid_balance
        mock_trigger.rsi_trigger.return_value = rsi_trigger
        mock_orders.place_buy_order.return_value = place_buy_order
        mock_orders.get_order_history.return_value = [{"avgPrice": last_order}]

        first_buy = FirstBuy(
            checkup=mock_checkup,
            trigger=mock_trigger,
            gatekeeper_storage=mock_gatekeeper_storage,
            orders=mock_orders,
            lines=mock_lines,
            metamanager=mock_metamanager,
            notifier=mock_notifier,
        )

        result = first_buy.activate()

        assert result == expect

        mock_checkup.valid_balance.assert_called_once()
        mock_trigger.rsi_trigger.assert_called_once()
        mock_orders.place_buy_order.assert_called_once()
        mock_lines.write_lines.assert_called_once_with(last_order)
        mock_notifier.send_buy_notify.assert_called_once_with(last_order)
        mock_checkup.update_orders_journal.assert_called_once_with(last_order)
        mock_metamanager.update_all.assert_called_once_with(type="first_buy")
