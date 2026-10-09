from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from app.models.expense import ExpenseType


class SplitInput(BaseModel):
    user_id: int
    amount: Decimal | None = None
    percentage: Decimal | None = None


class ExpenseCreate(BaseModel):
    paid_by: int
    amount: Decimal
    description: str
    split_type: ExpenseType
    splits: list[SplitInput]


class ExpenseResponse(BaseModel):
    id: int
    group_id: int
    paid_by: int
    paid_by_name:str
    amount: Decimal
    description: str
    split_type: ExpenseType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)