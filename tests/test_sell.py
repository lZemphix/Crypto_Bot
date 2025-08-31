import pytest
from unittest.mock import MagicMock, patch
from src.scripts.sell import Sell, Checkup, Notifier
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


#     @pytest.mark.parametrize(
#         "klines, avg_order, expect",
#         [
#             ([[0, 0, 0, 0, 130]], 150, True),  #    kline < avg_order
#             ([[0, 0, 0, 0, 130]], 120, False),  #   kline > avg_order
#             ([[0, 0, 0, 0, 130]], 130, False),  #   kline == avg_order
#             ([[0, 0, 0, 0, 130]], "str", None),  #  avg_order = str
#             ("str", 130, None),  #                  kline = str
#             ([], 130, None),  #                     kline = empty list
#             ([[0, 0, 0, 0, 130]], None, None),  #   avg_order = str
#             (None, 130, None),  #                   kline = None
#         ],
#     )
#     def test_valid_price(
#         self,
#         mock_orders,
#         mock_gatekeeper_storage,
#         avg_order,
#         klines,
#         mock_journal,
#         expect,
#     ):
#         mock_orders.get_avg_order.return_value = avg_order
#         mock_gatekeeper_storage.get_klines.return_value = klines
#         step_buy = 10.0
#         amount_buy = 12.0
#         checkup = Checkup(
#             mock_gatekeeper_storage,
#             mock_orders,
#             mock_journal,
#             amount_buy,
#             step_buy,
#         )

#         assert checkup.valid_price() == expect

#     def price_valid(self):      
#         actual_price = float(self.gatekeeper_storage.get_klines()[-2][4])
#         sell_price = self.orders.get_avg_order() + self.step_sell
#         return actual_price >= sell_price

# #     @pytest.mark.parametrize(
# #         "last_order, expect",
# #         [
# #             (12.0, True),
# #             (12, True),
# #             ("12.0", TypeError),
# #             (None, TypeError),
# #             ({1: 2}, TypeError),
# #             ([1, 2, 3], TypeError),
# #         ],
# #     )
# #     def test_update_orders_journal(
# #         self, mock_gatekeeper_storage, mock_orders, mock_journal, last_order, expect
# #     ):
# #         mock_journal.get.return_value = {
# #             "orders": [10.0, 11.0],
# #         }
# #         step_buy = 10.0
# #         amount_buy = 12.0
# #         checkup = Checkup(
# #             mock_gatekeeper_storage,
# #             mock_orders,
# #             mock_journal,
# #             amount_buy,
# #             step_buy,
# #         )
# #         if isinstance(expect, type) and issubclass(expect, BaseException):
# #             with pytest.raises(expect):
# #                 assert checkup.update_orders_journal(last_order=last_order)
# #         else:
# #             assert checkup.update_orders_journal(last_order=last_order) == expect


# # class TestNotifier:

# #     @pytest.fixture
# #     def mock_telenotify(self):
# #         return MagicMock()

# #     @pytest.fixture
# #     def mock_journal(self):
# #         return MagicMock()

# #     @pytest.fixture
# #     def mock_gatekeeper_storage(self):
# #         return MagicMock()

# #     # fmt: off
# #     @pytest.mark.parametrize(
# #             "balance, last_order, sell_lines, buy_lines, expect",
# #             [
# #                 ({"USDT": 12.0}, 10.0, [17.0, 22.0], [7.0, 2.0], True), #       Ok
# #                 (None, 10.0, [17.0, 22.0], [7.0, 2.0], AttributeError),#        balance == None
# #                 ([], 10.0, [17.0, 22.0], [7.0, 2.0], AttributeError),#          balance == list
# #                 ({}, 10.0, [17.0, 22.0], [7.0, 2.0], AttributeError),#          balance == empty dict
# #                 ({"USDT": 12.0}, 'str', [17.0, 22.0], [7.0, 2.0], TypeError),#  last_order != float
# #                 ({"USDT": 12.0}, 10.0, 'str', [7.0, 2.0], TypeError),#          sell_lines != list[float]
# #                 ({"USDT": 12.0}, 10.0, [17.0, 22.0], 'str', TypeError),#        buy_lines != list[float]
# #                 ({"12": 12.0}, 10.0, [17.0, 22.0], [7.0, 2.0], KeyError),#      balance not contains USDT
# #             ]
# #     )    
# #     # fmt: on
# #     def test_send_averaging_notify(
# #         self,
# #         last_order,
# #         mock_gatekeeper_storage,
# #         mock_journal,
# #         mock_telenotify,
# #         expect,
# #         sell_lines,
# #         buy_lines,
# #         balance,
# #     ):
        
# #         mock_gatekeeper_storage.get_balance.return_value = balance
# #         mock_telenotify.bought.return_value = 200
# #         mock_journal.get.return_value = {
# #             "sell_lines": sell_lines,
# #             "buy_lines": buy_lines,
# #         }
# #         notify = Notifier(mock_telenotify, mock_gatekeeper_storage, mock_journal)
# #         if isinstance(expect, type) and issubclass(expect, BaseException):
# #             with pytest.raises(expect):
# #                 assert notify.send_averaging_notify(last_order=last_order)
# #         else:
# #             notify.send_averaging_notify(last_order=last_order)
# #             expected_message = f'```\nAverage price: {last_order} USDT\nBalance: {balance["USDT"]}\nSell line: ${sell_lines[0]}\nAverage line: ${buy_lines[0]}```'
# #             mock_telenotify.bought.assert_called_once()
# #             mock_telenotify.bought.assert_called_once_with(expected_message)


# # class TestAveraging:

# #     @pytest.fixture
# #     def mock_lines(self):
# #         return MagicMock()

# #     @pytest.fixture
# #     def mock_gatekeeper_storage(self):
# #         return MagicMock()

# #     @pytest.fixture
# #     def mock_checkup(self):
# #         return MagicMock()

# #     @pytest.fixture
# #     def mock_trigger(self):
# #         return MagicMock()

# #     @pytest.fixture
# #     def mock_orders(self):
# #         return MagicMock()

# #     @pytest.fixture
# #     def mock_notifier(self):
# #         return MagicMock()

# #     @pytest.fixture
# #     def mock_metamanager(self):
# #         return MagicMock()
    
# #     @patch('src.scripts.averaging.time.sleep')
# #     @pytest.mark.parametrize(
# #         "valid_balance, valid_price, cross_dtu, update_balance, place_buy_order, update_orders_journal, write_lines, update_all, send_averaging_notify, expect",
# #         [
# #             (True, True, True, True, True, True, True, True, True, True),
# #             (False, True, True, True, True, True, True, True, True, None),
# #             (True, False, True, True, True, True, True, True, True, None),
# #             (True, True, False, True, True, True, True, True, True, None),
# #             (True, True, True, False, True, True, True, True, True, None),
# #             (True, True, True, True, False, True, True, True, True, None),
# #             (True, True, True, True, True, False, True, True, True, True),
# #             (True, True, True, True, True, True, False, True, True, True),
# #             (True, True, True, True, True, True, True, False, True, True),
# #             (True, True, True, True, True, True, True, True, False, True),
# #         ],
# #     )
# #     def test_activate(
# #         self,
# #         mock_sleep,
# #         valid_balance,
# #         valid_price,
# #         cross_dtu,
# #         update_balance,
# #         place_buy_order,
# #         update_orders_journal,
# #         write_lines,
# #         update_all,
# #         send_averaging_notify,
# #         mock_checkup,
# #         mock_trigger,
# #         mock_gatekeeper_storage,
# #         mock_orders,
# #         mock_lines,
# #         mock_metamanager,
# #         mock_notifier,
# #         expect,
# #     ):
# #         mock_checkup.valid_balance.return_value = valid_balance
# #         mock_checkup.valid_price.return_value = valid_price
# #         mock_checkup.update_orders_journal.return_value = update_orders_journal
# #         mock_trigger.cross_down_to_up.return_value = cross_dtu
# #         mock_gatekeeper_storage.update_balance.return_value = update_balance
# #         mock_orders.place_buy_order.return_value = place_buy_order
# #         mock_lines.write_lines.return_value = write_lines
# #         mock_metamanager.update_all.return_value = update_all
# #         mock_notifier.send_averaging_notify.return_value = send_averaging_notify

# #         averaging = Averaging(
# #             mock_lines,
# #             mock_checkup,
# #             mock_trigger,
# #             mock_gatekeeper_storage,
# #             mock_orders,
# #             mock_metamanager,
# #             mock_notifier,
# #         )

# #         if isinstance(expect, type) and issubclass(expect, BaseException):
# #             with pytest.raises(expect):
# #                 assert averaging.activate()
# #         else:
# #             assert averaging.activate() == expect
