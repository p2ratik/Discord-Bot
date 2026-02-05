from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.user import User
from app.models.role import Role as RoleModel
from app.schemas.user import UserCreate, UserUpdate, UserWithRoles
from typing import List, Optional


async def get_user(user_id: str, db: AsyncSession) -> Optional[User]:
    """
    Get a single user by user_id
    
    :param user_id: User ID to fetch
    :type user_id: str
    :param db: Database session
    :type db: AsyncSession
    :return: User object or None
    """
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_all_users(db: AsyncSession) -> List[User]:
    """
    Get all users
    
    :param db: Database session
    :type db: AsyncSession
    :return: List of User objects
    """
    result = await db.execute(select(User))
    return result.scalars().all()


async def create_user(user_data: UserCreate, db: AsyncSession) -> User:
    """
    Create a new user
    
    :param user_data: User data to create
    :type user_data: UserCreate
    :param db: Database session
    :type db: AsyncSession
    :return: Created User object
    :raises HTTPException: If user_id already exists (409)
    """
    try:
        db_user = User(**user_data.model_dump())
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f"User with user_id '{user_data.user_id}' already exists")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


async def update_user(user_id: str, user_data: UserUpdate, db: AsyncSession) -> Optional[User]:
    """
    Update a user
    
    :param user_id: User ID to update
    :type user_id: str
    :param user_data: Updated user data
    :type user_data: UserUpdate
    :param db: Database session
    :type db: AsyncSession
    :return: Updated User object or None if not found
    """
    try:
        user = await get_user(user_id, db)
        if not user:
            return None
        
        # Update only provided fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")


async def delete_user(user_id: str, db: AsyncSession) -> bool:
    """
    Delete a user
    
    :param user_id: User ID to delete
    :type user_id: str
    :param db: Database session
    :type db: AsyncSession
    :return: True if deleted, False if not found
    """
    try:
        user = await get_user(user_id, db)
        if not user:
            return False
        
        await db.delete(user)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")


async def get_user_with_roles(user_id: str, db: AsyncSession) -> Optional[UserWithRoles]:
    """
    Get user with their role data
    
    :param user_id: User ID to fetch
    :type user_id: str
    :param db: Database session
    :type db: AsyncSession
    :return: UserWithRoles object or None
    """
    user = await get_user(user_id, db)
    if not user:
        return None
    
    # Fetch role data
    role_result = await db.execute(
        select(RoleModel).where(RoleModel.user_id == user_id)
    )
    role = role_result.scalar_one_or_none()
    
    # Convert to UserWithRoles
    user_dict = {
        "id": user.id,
        "user_id": user.user_id,
        "username": user.username,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "role": role.role if role else None
    }
    
    return UserWithRoles(**user_dict)
