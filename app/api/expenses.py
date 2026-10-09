from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.group import GroupMember
from app.models.expense import Expense, ExpenseType
from app.models.split import Split
from app.schemas.expense import ExpenseCreate, ExpenseResponse

router = APIRouter(tags=["Expenses"])


@router.post(
    "/{group_id}/expenses",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_expense(
    group_id: int,
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a new expense to the group and record how it should be split
    """
                                                    
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
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
            GroupMember.user_id == expense_data.paid_by,
        )
    )
    paid_by_member = result.scalars().first()

    if not paid_by_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paid by user is not a member of this group"
        )

                        
    if expense_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0"
        )

                                   
    if not expense_data.splits:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one split is required"
        )

                                                  
    if expense_data.split_type == ExpenseType.EXACT:
        for split in expense_data.splits:
            if split.amount is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Amount is required for exact split"
                )
        
                                       
        total_split = sum(s.amount for s in expense_data.splits if s.amount is not None)
        if total_split != expense_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Split amounts must sum to {expense_data.amount}, got {total_split}"
            )

    elif expense_data.split_type == ExpenseType.PERCENTAGE:
        for split in expense_data.splits:
            if split.percentage is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Percentage is required for percentage split"
                )
        
                              
        total_pct = sum(s.percentage for s in expense_data.splits if s.percentage is not None)
        if total_pct != 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Percentages must sum to 100, got {total_pct}"
            )

                                                 
    for split in expense_data.splits:
        result = await db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == split.user_id
            )
        )
        if not result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {split.user_id} is not a member of this group"
            )

                       
    expense = Expense(
        group_id=group_id,
        paid_by=expense_data.paid_by,
        amount=expense_data.amount,
        description=expense_data.description,
        split_type=expense_data.split_type
    )
    db.add(expense)
    await db.commit()
    await db.refresh(expense)

                                              
    if expense_data.split_type == ExpenseType.EQUAL:
                                                       
        split_amount = expense_data.amount / len(expense_data.splits)
        for split_data in expense_data.splits:
            split = Split(
                expense_id=expense.id,
                user_id=split_data.user_id,
                amount=split_amount
            )
            db.add(split)

    elif expense_data.split_type == ExpenseType.EXACT:
                                                      
        for split_data in expense_data.splits:
            split = Split(
                expense_id=expense.id,
                user_id=split_data.user_id,
                amount=split_data.amount
            )
            db.add(split)

    elif expense_data.split_type == ExpenseType.PERCENTAGE:
                                             
        for split_data in expense_data.splits:
            split_amount = (expense_data.amount * split_data.percentage) / 100
            split = Split(
                expense_id=expense.id,
                user_id=split_data.user_id,
                amount=split_amount
            )
            db.add(split)

                            
    await db.commit()

    return expense


@router.get("/{group_id}/expenses", response_model=list[ExpenseResponse])
async def get_group_expenses(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    View all expenses recorded in the group.
    """
                                                 
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
        )
    )
    membership = result.scalars().first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group"
        )

                                        
    result = await db.execute(
        select(Expense).where(
            Expense.group_id == group_id,
            Expense.paid_by == current_user.id,
                              )
    )
    expenses = result.scalars().all()

    response = []

    for expense in expenses:
        paid_by_user = await db.get(User, expense.paid_by)
    
        response.append({
        "id": expense.id,
        "group_id": expense.group_id,
        "paid_by": expense.paid_by,
        "paid_by_name": paid_by_user.name,
        "amount": expense.amount,
        "description": expense.description,
        "split_type": expense.split_type,
        "created_at": expense.created_at
    })
    return response
