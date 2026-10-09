from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class SplitResponse(BaseModel):
    id: int
    expense_id: int
    user_id: int
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)