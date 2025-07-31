from enum import Enum
import enum


class ActionType(Enum):
    FIRST_BUY = enum.auto()
    AVERAGE = enum.auto()
    SELL = enum.auto()
