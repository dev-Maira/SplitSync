from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.group import GroupMember
from app.models.settlement import Settlement
from app.schemas.settlement import SettlementCreate, SettlementResponse
from app.services.balance_service import get_group_balances


router = APIRouter(tags=["Settlements"])


@router.post("/{group_id}/settle", response_model=SettlementResponse, status_code=status.HTTP_201_CREATED)
async def create_settlement(
    group_id: int,
    settlement_data: SettlementCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a settlement — the current user has paid the amount owed to the recipient.    
    """
    
                                                
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id
        )
    )
    membership = result.scalars().first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group"
        )
    
                                                    
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == settlement_data.received_by
        )
    )
    received_membership = result.scalars().first()
    
    if not received_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Received by user is not a member of this group"
        )
    
                                                                
    balances = await get_group_balances(group_id, db)
    current_user_balance = balances.get(current_user.id, 0)
    
    amount_owed = abs(current_user_balance) if current_user_balance < 0 else 0
    
    if amount_owed == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't owe anything in this group"
        )
    
    if settlement_data.amount > amount_owed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You owe {amount_owed}, cannot settle for {settlement_data.amount}"
        )
    
                                    
    settlement = Settlement(
        group_id=group_id,
        paid_by=current_user.id,
        received_by=settlement_data.received_by,
        amount=settlement_data.amount
    )
    
    db.add(settlement)
    await db.commit()
    await db.refresh(settlement)
    
    return settlement


@router.get("/{group_id}/settlements", response_model=list[SettlementResponse])
async def get_settlements(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    View the settlement history for the entire group.
    """
    
                              
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id
        )
    )
    membership = result.scalars().first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group"
        )
    
                                              
    result = await db.execute(
        select(Settlement).where(Settlement.group_id == group_id)
    )
    settlements = result.scalars().all()
    
                    
    return settlements