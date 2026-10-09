from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.group import GroupMember
from app.models.expense import Expense, ExpenseType
from app.models.split import Split
from app.schemas.expense import ExpenseCreate, ExpenseResponse
from app.models.settlement import Settlement

async def get_group_balances(group_id:int, db:AsyncSession = Depends(get_db)):
   
    
                                               
    member =  await db.execute(select(GroupMember).where(GroupMember.group_id == group_id))
    members = member.scalars().all()
    if not members:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Group not found"
            )

    balances = {}

    for memb in members:
          balances[memb.user_id] = Decimal(0)


    expenses = await db.execute(select(Expense).where(Expense.group_id == group_id))

    for expense in expenses.scalars().all():
        balances[expense.paid_by] += expense.amount
        
                               
        result = await db.execute(select(Split).where(Split.expense_id == expense.id))
        splits = result.scalars().all()
    
    for split in splits:
        balances[split.user_id] -= split.amount

                                                                   
    settlements = await db.execute(select(Settlement).where(group_id == group_id))

    for settlement in settlements:
                                                           
        balances[settlement.paid_by] -= settlement.amount
        
                                                               
        balances[settlement.received_by] += settlement.amount
    
                                                         
    return {user_id: amount for user_id, amount in balances.items() if amount != 0}





















