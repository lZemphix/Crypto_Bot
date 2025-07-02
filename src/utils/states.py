import enum


class BotState(enum.Enum):
    FIRST_BUY = enum.auto()
    WAITING = enum.auto()
    SELL = enum.auto()
    AVERAGING = enum.auto()
    STOPPED = enum.auto()
    NEM = enum.auto()

    @staticmethod
    def transitions() -> dict:
        transitions = {
            BotState.FIRST_BUY: [BotState.SELL, BotState.STOPPED, BotState.AVERAGING],
            BotState.AVERAGING: [BotState.SELL, BotState.STOPPED],
            BotState.SELL: [BotState.STOPPED, BotState.FIRST_BUY],
            BotState.STOPPED: [BotState.FIRST_BUY],
        }
        return transitions


class BuyState(enum.Enum):
    WAITING = enum.auto()
    BALANCE_CORRECT = enum.auto()
    PRICE_CORRECT = enum.auto()
    STOPPED = enum.auto()

    @staticmethod
    def transitions() -> dict:
        transitions = {
            BuyState.WAITING: [BuyState.STOPPED, BuyState.BALANCE_CORRECT],
            BuyState.BALANCE_CORRECT: [BuyState.PRICE_CORRECT],
            BuyState.PRICE_CORRECT: [BuyState.STOPPED],
        }
        return transitions


class SellState(enum.Enum):
    WAITING = enum.auto()
    PRICE_CORRECT = enum.auto()
    STOPPED = enum.auto()

    @staticmethod
    def transitions() -> dict:
        transitions = {
            SellState.WAITING: [SellState.STOPPED, SellState.PRICE_CORRECT],
            SellState.PRICE_CORRECT: [SellState.STOPPED],
        }
        return transitions
