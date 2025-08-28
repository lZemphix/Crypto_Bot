from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from .schemas import ActionType


class Base(DeclarativeBase):
    pass


class Actions(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(default=datetime.now())
    action_type: Mapped[ActionType] = mapped_column()
    pil: Mapped[float] = mapped_column()
