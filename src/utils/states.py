import enum


class BotState(enum.Enum):
    FIRST_BUY = enum.auto()
    WAITING = enum.auto()
    SELL = enum.auto()
    AVERAGING = enum.auto()
    STOPPED = enum.auto()
    NEM = enum.auto()


class BuyState(enum.Enum):
    WAITING = enum.auto()
    BALANCE_CORRECT = enum.auto()
    PRICE_CORRECT = enum.auto()
    STOPPED = enum.auto()


class SellState(enum.Enum):
    WAITING = enum.auto()
    PRICE_CORRECT = enum.auto()
    STOPPED = enum.auto()
