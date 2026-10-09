from pydantic import BaseModel, ConfigDict,EmailStr
from datetime import datetime
from app.models.group import GroupRole


class GroupCreate(BaseModel):
    name: str

class GroupResponse(BaseModel):
    id: int
    name: str
    created_by: int
    created_by_name:str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GroupMemberResponse(BaseModel):
    id: int
    group_id: int
    user_id: int
    user_name:str
    role: GroupRole

    model_config = ConfigDict(from_attributes=True)

class AddMemberRequest(BaseModel):
    email: EmailStr    