from sqlalchemy import String, Integer,DateTime, func,ForeignKey,UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
import enum
from sqlalchemy import Enum as SQLEnum
import datetime

class GroupRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"

class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name : Mapped[str] = mapped_column(String(100),index=True, nullable=False)
    created_by : Mapped[int] = mapped_column(Integer,ForeignKey("users.id"),index=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
class GroupMember(Base):

    __tablename__ = "group_members"

    id: Mapped[int] = mapped_column(Integer,primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"),nullable=False )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    role: Mapped[GroupRole] = mapped_column(SQLEnum(GroupRole), nullable=False, default=GroupRole.MEMBER)

    __table_args__ = (
            UniqueConstraint("group_id", "user_id", name="uq_group_user"),                                                                                            
        )

