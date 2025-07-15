from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Statistic(Base):
    __tablename__ = "statistic"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(default=datetime.now())
    balance: Mapped[float] = mapped_column()
    actions: Mapped[int] = mapped_column(default=0)
    profit: Mapped[float] = mapped_column(default=0)
