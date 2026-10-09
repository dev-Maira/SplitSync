from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal

class SettlementCreate(BaseModel):
    amount:Decimal
    received_by: int

class SettlementResponse(BaseModel):
    id:int
    group_id:int
    paid_by:int
    received_by:int
    amount:Decimal
    created_at:datetime

    model_config = ConfigDict(from_attributes=True)
