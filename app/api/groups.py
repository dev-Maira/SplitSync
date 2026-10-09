from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.group import Group, GroupMember, GroupRole
from app.schemas.group import (
    GroupCreate,
    GroupResponse,
    GroupMemberResponse,
    AddMemberRequest
)

router = APIRouter(tags=["Groups"])


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new group with the current user as its admin
    """
    group = Group(
        name=group_data.name,
        created_by=current_user.id
    )

    db.add(group)
    await db.commit()
    await db.refresh(group)

    group_member = GroupMember(
        group_id=group.id,
        user_id=current_user.id,
        role=GroupRole.ADMIN
    )

    db.add(group_member)
    await db.commit()
    await db.refresh(group_member)

    return {
        "id": group_member.id,
        "group_id": group_member.group_id,
        "user_id": group_member.user_id,
        "user_name": current_user.name,  
        "role": group_member.role
    }

@router.get("/", response_model=list[GroupResponse])
async def get_my_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    View all groups.
    """
    result = await db.execute(
        select(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .where(GroupMember.user_id == current_user.id)
    )

    groups = result.scalars().all()
    response_list = []
    for group in groups:
        creator = await db.get(User, group.created_by)
        response_list.append({
            "id": group.id,
            "name": group.name,
            "created_by": group.created_by,
            "created_by_name": creator.name,  
            "created_at": group.created_at
        })
    
    return response_list


@router.post(
    "/{group_id}/members",
    response_model=GroupMemberResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_member(
    group_id: int,
    member_data: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a new member to the group.
    """
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
            GroupMember.role == GroupRole.ADMIN
        )
    )

    admin_check = result.scalars().first()

    if not admin_check:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group admins can perform this action"
        )

    result = await db.execute(
        select(User).where(User.email == member_data.email)
    )

    target_user = result.scalars().first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == target_user.id
        )
    )

    existing_member = result.scalars().first()

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this group"
        )

    group_member = GroupMember(
        group_id=group_id,
        user_id=target_user.id,
        role=GroupRole.MEMBER
    )

    db.add(group_member)
    await db.commit()
    await db.refresh(group_member)

    return {
    "id": group_member.id,
    "group_id": group_member.group_id,
    "user_id": group_member.user_id,
    "user_name": target_user.name,  
    "role": group_member.role
}

@router.delete(
    "/{group_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def remove_member(
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a member from the group.
    """
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
            GroupMember.role == GroupRole.ADMIN
        )
    )

    admin = result.scalars().first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group admins can remove members"
        )

    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        )
    )

    member = result.scalars().first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this group"
        )

    if member.role == GroupRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group admin cannot be removed"
        )

                      
    await db.delete(member)

                     
    await db.commit()

    return None

@router.get("/{group_id}/members", response_model=list[GroupMemberResponse])
async def get_group_members(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    View all members of a group.
    """
    result = await db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user.id,
            )
    )
    
    members = result.scalars().all() 
    if not members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group"
        )
    result = await db.execute(
        select(GroupMember).where(GroupMember.group_id == group_id)
    )
    members = result.scalars().all()

    response_list = []
    for member in members:
        user = await db.get(User, member.user_id)
        response_list.append({
            "id": member.id,
            "group_id": member.group_id,
            "user_id": member.user_id,
            "user_name": user.name,
            "role": member.role
        })
    
    return response_list
   

 