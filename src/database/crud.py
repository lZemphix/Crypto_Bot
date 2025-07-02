import datetime
from logging import getLogger
from .core import sync_session, engine
from .models import Statistic, Base

logger = getLogger(__name__)

class Tables:

    def unworked(id: int, date: datetime.datetime, balance: float, actions: int, profit: float):
        with sync_session.begin() as conn:
            statistic = Statistic(
                id=id, date=date, balance=balance, actions=actions, profit=profit
            )
            conn.add(statistic)
            conn.commit()
