from sqlalchemy import Integer,Numeric,ForeignKey,UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

from decimal import Decimal

class Split(Base):
    __tablename__ = "splits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    expense_id : Mapped[int] = mapped_column(ForeignKey("expenses.id", ondelete="CASCADE"),nullable=False )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    __table_args__ = (
            UniqueConstraint("expense_id","user_id", name="uq_expense_user"),
        )