from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import attributes
from fastapi import HTTPException
from app.models.admin import Admin
from app.schemas.admin import adminRole , adminRoleAdd, adminRolePatch
from app.utils.logger import get_logger
from typing import Optional

logger = get_logger(__name__)

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
        logger.debug(f"Fetching admin role for user: {user_id}")
        results = await db.execute(select(Admin).where(Admin.user_id == user_id))
        admin = results.scalar_one_or_none()
        if admin:
            logger.info(f"Found admin role for user {user_id}")
        else:
            logger.debug(f"No admin role found for user {user_id}")
        return admin
    except Exception as e:
        logger.error(f"Error fetching admin role for user {user_id}: {e}", exc_info=True)
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
        logger.info(f"Adding admin role for user: {role.user_id}")
        db_role = Admin(**role.model_dump())
        db.add(db_role)

        await db.commit()
        await db.refresh(db_role)

        logger.info(f"Successfully added admin role for user {role.user_id}")
        return db_role
    
    except Exception as e:
        logger.error(f"Error adding admin role for user {role.user_id}: {e}", exc_info=True)
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
        logger.info(f"Patching admin role for user: {user_id}")
        current_data = await get_role_for_admin(user_id, db)

        if not current_data:
            logger.warning(f"Cannot patch admin role - user {user_id} not found")
            return None
        
        current_role = current_data.role or {}
        current_role.update(role.role)
        current_data.role = current_role

        # Mark the JSON column as modified so SQLAlchemy detects the change
        attributes.flag_modified(current_data, 'role')

        await db.commit()
        await db.refresh(current_data)
        
        logger.info(f"Successfully patched admin role for user {user_id}")
        return current_data
    except Exception as e:
        await db.rollback()
        logger.error(f"Error patching admin role for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating admin role: {str(e)}")




