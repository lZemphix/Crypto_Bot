
import pytest
from utils.exceptions import (
    NoCryptoCurrencyException,
    IncorrectOrdersHistory,
    IncorrectOpenOrdersList,
    OrderPlaceException,
)
from utils.states import BotState, BuyState, SellState


def test_exceptions():
    with pytest.raises(NoCryptoCurrencyException):
        raise NoCryptoCurrencyException("Test")
    with pytest.raises(IncorrectOrdersHistory):
        raise IncorrectOrdersHistory("Test")
    with pytest.raises(IncorrectOpenOrdersList):
        raise IncorrectOpenOrdersList("Test")
    with pytest.raises(OrderPlaceException):
        raise OrderPlaceException("Test")


def test_bot_state():
    assert BotState.FIRST_BUY
    assert BotState.WAITING
    assert BotState.SELL
    assert BotState.AVERAGING
    assert BotState.STOPPED
    assert BotState.NEM


def test_buy_state():
    assert BuyState.WAITING
    assert BuyState.BALANCE_CORRECT
    assert BuyState.PRICE_CORRECT
    assert BuyState.STOPPED


def test_sell_state():
    assert SellState.WAITING
    assert SellState.PRICE_CORRECT
    assert SellState.STOPPED



