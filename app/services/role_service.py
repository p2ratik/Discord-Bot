from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import attributes
from fastapi import HTTPException
from app.models.role import Role as RoleModel
from app.schemas.role import RoleCreate, RolePatch
from typing import Optional


async def get_roles_for_user(user_id: str, db: AsyncSession) -> Optional[RoleModel]:
    """
    Get roles for a specific user
    
    :param user_id: User ID to fetch roles for
    :type user_id: str
    :param db: Database session
    :type db: AsyncSession
    :return: Role object or None
    """
    try:
        results = await db.execute(
            select(RoleModel).where(RoleModel.user_id == user_id)
        )
        return results.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching roles: {str(e)}")


async def add_role(role: RoleCreate, db: AsyncSession) -> RoleModel:
    """
    Add a new role for a user
    
    :param role: Role data to add
    :type role: RoleCreate
    :param db: Database session
    :type db: AsyncSession
    :return: Created role object
    :raises HTTPException: If role already exists for user (409)
    """
    try:
        db_role = RoleModel(**role.model_dump())
        db.add(db_role)
        
        await db.commit()
        await db.refresh(db_role)
        
        return db_role
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail=f"Role already exists for user_id '{role.user_id}'")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding role: {str(e)}")


async def patch_role(user_id: str, role_patch: RolePatch, db: AsyncSession) -> Optional[RoleModel]:
    """
    Partially update a role (PATCH semantics - only update provided fields)
    
    :param user_id: User ID to update role for
    :type user_id: str
    :param role_patch: Partial role data to update
    :type role_patch: RolePatch
    :param db: Database session
    :type db: AsyncSession
    :return: Updated role object or None if not found
    """
    try:
        role = await get_roles_for_user(user_id, db)
        
        if not role:
            return None
        
        # Merge updates into existing role data (PATCH semantics)
        current_data = role.role or {}
        current_data.update(role_patch.role)
        role.role = current_data
        
        # Mark the JSON column as modified so SQLAlchemy detects the change
        attributes.flag_modified(role, 'role')
        
        await db.commit()
        await db.refresh(role)
        
        return role
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating role: {str(e)}")


async def remove_role(user_id: str, db: AsyncSession) -> bool:
    """
    Remove a role for a user
    
    :param user_id: User ID to remove role for
    :type user_id: str
    :param db: Database session
    :type db: AsyncSession
    :return: True if successful, False if not found
    """
    try:
        result = await db.execute(
            select(RoleModel).where(RoleModel.user_id == user_id)
        )
        role = result.scalar_one_or_none()
        
        if role:
            await db.delete(role)
            await db.commit()
            return True
        return False
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error removing role: {str(e)}")


# async def update_roles(user_id:str , Payload:RolePatch, db: AsyncSession):
#     """
#     Docstring for update_roles
    
#     :param user_id: Description
#     :type user_id: str
#     :param Payload: Description
#     :type Payload: RolePatch
#     """
#     try:
#         results = await db.execute(
#             select(RoleModel).where(RoleModel.user_id == user_id)
#         )
#         user = results.scalar_one_or_none()

#         if not user:
#             return False
        
#         roles = user.roles or {}

#         roles[Payload.roles] = Payload.value

