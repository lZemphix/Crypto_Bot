from logging import getLogger

from .schemas import ActionType
from .core import sync_session
from .models import Actions
from sqlalchemy import select

logger = getLogger(__name__)


class ActionsTable:

    @staticmethod
    def add_action(action_type: ActionType, pil: float):
        with sync_session() as conn:
            action = Actions(action_type=action_type, pil=pil)
            conn.add(action)
            conn.commit()

    @staticmethod
    def get_all_actions():
        with sync_session() as conn:
            stmt = select(Actions)
            action = conn.execute(stmt)
            return action.scalars().all()
