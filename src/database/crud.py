import datetime
from logging import getLogger
from .core import sync_session, engine
from .models import Statistic, Base
from sqlalchemy import select

logger = getLogger(__name__)


class StatisticTable:
    
    @staticmethod
    def add_statistic(balance: float, actions: int = 0, profit: float = 0):
        with sync_session() as conn:
            statistic = Statistic(
                balance=balance, actions=actions, profit=profit
            )
            conn.add(statistic)
            conn.commit()

    @staticmethod
    def get_all_statistic():
        with sync_session() as conn:
            stmt = select(Statistic)
            statistic = conn.execute(stmt)
            return statistic.scalars().all()