import datetime
from sqlalchemy import Integer,DateTime, func,ForeignKey,Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from decimal import Decimal

class Settlement(Base):
    __tablename__ = 'settlements'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"),nullable=False )
    paid_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    received_by : Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


