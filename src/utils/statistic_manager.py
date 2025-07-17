from database.crud import StatisticTable
import datetime


class DateManager:
    def __init__(self):
        pass

    def date_delta(self) -> bool:
        last_stat = (StatisticTable().get_all_statistic())[-1]
        delta = datetime.datetime.now() - last_stat.date
        one_day = datetime.timedelta(days=1)
        if delta >= one_day:
            return True
        else:
            return False
    
class StatisticManager:
    def __init__(self):
        self.dateM = DateManager()

    def add_statistic(self, balance: float, actions: int, profit: float):
        if self.dateM.date_delta():
            StatisticTable().add_statistic(
                balance=balance, actions=actions, profit=profit
                )
