from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import attributes
from fastapi import HTTPException
from app.models.admin import Admin
from app.schemas.admin import adminRole , adminRoleAdd, adminRolePatch
from typing import Optional

# Function to get admin role
async def get_role_for_admin(user_id : str, db:AsyncSession)->Optional[Admin]:
    """
    Get admin role for a specific user
    
    :param user_id: User ID to fetch admin role for
    :type user_id: str
    :param db: Database session
    :type db: AsyncSession
    :return: Admin object or None if not found
    """
    try:
        results = await db.execute(select(Admin).where(user_id == Admin.user_id))
        return results.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching admin role: {str(e)}")

# Function to add admin roles into the database
async def add_role_for_admin(role : adminRoleAdd, db:AsyncSession):
    """
    Docstring for add_role_for_admin
    
    :param role: Description
    :type role: adminRoleAdd
    :param db: Description
    :type db: AsyncSession
    """
    try:
        db_role = Admin(**role.model_dump())
        db.add(db_role)

        await db.commit()
        await db.refresh(db_role)

        return db_role
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Role not added: {str(e)}")
    
# Function to update admin roles     
async def patch_role_for_user(user_id: str, role : adminRolePatch, db:AsyncSession):
    """
    Docstring for patch_role_for_user
    
    :param role: Description
    :type role: adminRolePatch
    :param db: Description
    :type db: AsyncSession
    """
    try:
        current_data = await get_role_for_admin(user_id, db)

        if not current_data:
            return None
        
        current_role = current_data.role or {}
        current_role.update(role.role)
        current_data.role = current_role

        # Mark the JSON column as modified so SQLAlchemy detects the change
        attributes.flag_modified(current_data, 'role')

        await db.commit()
        await db.refresh(current_data)
        return current_data
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating admin role: {str(e)}")




