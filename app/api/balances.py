from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.group import GroupMember
from app.schemas.balance import BalanceResponse, GroupBalanceResponse
from app.services.balance_service import get_group_balances
from app.services.debt_simplifier import simplify_debts


router = APIRouter(tags=["Balances"])


@router.get("/{group_id}/balance", response_model=GroupBalanceResponse)
async def get_group_balance(group_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    View the current balances of all members in the group
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

                                    
    balances_dict = await get_group_balances(group_id, db)
    balances_list = []

    for user_id, amount in balances_dict.items():
        user = await db.get(User, user_id)

        
        balances_list.append({
            "user_id": user_id,
            "user_name": user.name,
            "amount": amount
        })

    return {
        "group_id": group_id,
        "balances": balances_list
    }
    


@router.get("/{group_id}/balance/me", response_model=BalanceResponse)
async def get_my_balance(group_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    View the current user’s balance in the group.
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

    balances_dict = await get_group_balances(group_id, db)
    my_balance = balances_dict.get(current_user.id, 0)
    return {
            "user_id": current_user.id,
            "amount": my_balance
        }


@router.get("/{group_id}/simplified")
async def get_simplified_settlements(group_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    View the simplified payments needed to settle all outstanding debts.
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

    balances_dict = await get_group_balances(group_id, db)
    transactions = simplify_debts(balances_dict)

    return {
            "group_id": group_id,
            "settlements": transactions
        }