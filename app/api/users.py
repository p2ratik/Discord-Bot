from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserWithRoles
from app.services.user_service import (
    get_user,
    get_all_users,
    create_user,
    update_user,
    delete_user,
    get_user_with_roles
)
from app.db.session import get_db
from typing import List

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    """
    Get all users
    
    :param db: Database session
    :type db: AsyncSession
    :return: List of users
    """
    users = await get_all_users(db)
    return users


@router.get("/{user_id}", response_model=UserWithRoles)
async def get_user_endpoint(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get a specific user with their role data
    
    :param user_id: User ID
    :type user_id: str
    :param db: Database session
    :type db: AsyncSession
    :return: User with roles
    :raises HTTPException: 404 if user not found
    """
    user = await get_user_with_roles(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with user_id '{user_id}' not found")
    return user


@router.post("", response_model=UserResponse, status_code=201)
async def create_user_endpoint(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user
    
    :param user_data: User data
    :type user_data: UserCreate
    :param db: Database session
    :type db: AsyncSession
    :return: Created user
    :raises HTTPException: 409 if user_id already exists
    """
    user = await create_user(user_data, db)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user
    
    :param user_id: User ID
    :type user_id: str
    :param user_data: Updated user data
    :type user_data: UserUpdate
    :param db: Database session
    :type db: AsyncSession
    :return: Updated user
    :raises HTTPException: 404 if user not found
    """
    user = await update_user(user_id, user_data, db)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with user_id '{user_id}' not found")
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user_endpoint(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete a user
    
    :param user_id: User ID
    :type user_id: str
    :param db: Database session
    :type db: AsyncSession
    :raises HTTPException: 404 if user not found
    """
    success = await delete_user(user_id, db)
    if not success:
        raise HTTPException(status_code=404, detail=f"User with user_id '{user_id}' not found")
