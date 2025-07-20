from logging import getLogger
from utils.gatekeeper import gatekeeper
from client.base import BotBase
from utils.klines_manager import KlinesManager
import ta.momentum


logger = getLogger(__name__)


class IndicatorTrigger(BotBase):
    def __init__(self):
        super().__init__()
        self.klines = KlinesManager()

    def rsi_trigger(self) -> bool:
        try:
            df = self.klines.get_klines_dataframe()
            current_rsi = ta.momentum.rsi(df.close).iloc[-1]
            return current_rsi <= self.RSI
        except ValueError:
            logger.warning("rsi trigger returned invalid data")
            return False


class CrossKlinesTrigger(BotBase):

    def __init__(self):
        super().__init__()

    def get_klines(self) -> tuple[float, float]:
        klines = gatekeeper.get_klines()
        current_kline = float(klines[-1][4])
        prev_kline = float(klines[-2][4])
        return current_kline, prev_kline

    def get_lines(self) -> tuple[list[float], list[float]]:
        buy_lines = self.journal.get()["buy_lines"]
        sell_lines = self.journal.get()["sell_lines"]
        return buy_lines, sell_lines

    def cross_down_to_up(self) -> bool:  # Покупка
        current_kline, prev_kline = self.get_klines()
        buy_lines: list[float] = self.get_lines()[0]
        for buy_line in buy_lines[::-1]:
            if prev_kline < buy_line <= current_kline:
                return True
        return False

    def cross_up_to_down(self) -> bool:  # Продажа
        current_kline, prev_kline = self.get_klines()
        sell_lines: list[float] = self.get_lines()[1]
        for sell_line in sell_lines[::-1]:
            if prev_kline > sell_line >= current_kline:
                return True
        return False


class BalanceTrigger(BotBase):
    def __init__(self):
        super().__init__()

    def invalid_balance(self) -> bool:
        balance = gatekeeper.get_balance()["USDT"]
        if balance < self.amount_buy:
            return True
