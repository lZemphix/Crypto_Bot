from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Statistic(Base):
    __tablename__ = "statistic"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column()
    balance: Mapped[float] = mapped_column()
    actions: Mapped[int] = mapped_column(default=0)
    profit: Mapped[float] = mapped_column()
