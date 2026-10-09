from pydantic import BaseModel,EmailStr,Field,ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    name:str
    email:EmailStr
    password:str = Field(min_length=8)

class UserResponse(BaseModel):
    id:int
    name:str
    email:EmailStr
    created_at:datetime    

    model_config = ConfigDict(from_attributes=True)