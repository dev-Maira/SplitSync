from sqlalchemy import Integer,ForeignKey,Numeric,String,DateTime, func
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
import enum
from sqlalchemy import Enum as SQLEnum
import datetime

class ExpenseType(str, enum.Enum):
    EQUAL ="equal"
    EXACT = "exact"
    PERCENTAGE = "percentage"

class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"),nullable=False )
    paid_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(String,nullable=False)
    split_type: Mapped[ExpenseType] = mapped_column(SQLEnum(ExpenseType),nullable=False,default=ExpenseType.EQUAL)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    