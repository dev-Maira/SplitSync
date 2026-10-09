from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import List

class BalanceResponse(BaseModel):                      
    user_id: int
    user_name:str
    amount:Decimal

    model_config = ConfigDict(from_attributes=True)

class GroupBalanceResponse(BaseModel):              
    group_id: int
    balances: List[BalanceResponse]    