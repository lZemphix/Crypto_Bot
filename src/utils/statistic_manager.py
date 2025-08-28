from database.crud import StatisticTable
import datetime


class DateManager:
    def __init__(self):
        pass

    def date_delta(self) -> bool:
        stats = StatisticTable().get_all_statistic()
        if not stats:
            return True
        last_stat = stats[-1]
        delta = datetime.datetime.now() - last_stat.date
        one_day = datetime.timedelta(days=1)
        if delta >= one_day:
            return True
        return False


class StatisticManager:
    def __init__(self):
        self.dateM = DateManager()

    def add_statistic(self, balance: float, actions: int, profit: float) -> None:
        if self.dateM.date_delta():
            StatisticTable().add_statistic(
                balance=balance, actions=actions, profit=profit
            )
