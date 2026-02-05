from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.role import Role, RoleCreate, RolePatch
from app.services.role_service import get_roles_for_user, add_role, remove_role, patch_role
from app.db.session import get_db

router = APIRouter(prefix="/api", tags=["roles"])


@router.post('/role', response_model=Role, status_code=201)
async def add_role_endpoint(role: RoleCreate, db: AsyncSession = Depends(get_db)):
    """
    Add a new role for a user
    
    :param role: Role data
    :type role: RoleCreate
    :param db: Database session
    :type db: AsyncSession
    :return: Created role object
    :raises HTTPException: 409 if role already exists for user
    """
    return await add_role(role, db)


@router.get('/role/{user_id}', response_model=Role)
async def get_roles_endpoint(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get roles for a specific user
    
    :param user_id: User ID
    :type user_id: str
    :param db: Database session
    :type db: AsyncSession
    :return: Role object
    :raises HTTPException: 404 if role not found
    """
    role = await get_roles_for_user(user_id, db)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role not found for user_id '{user_id}'")
    return role


@router.patch('/role/{user_id}', response_model=Role)
async def patch_role_endpoint(
    user_id: str,
    role_patch: RolePatch,
    db: AsyncSession = Depends(get_db)
):
    """
    Partially update a role (PATCH semantics)
    
    :param user_id: User ID
    :type user_id: str
    :param role_patch: Partial role data to update
    :type role_patch: RolePatch
    :param db: Database session
    :type db: AsyncSession
    :return: Updated role object
    :raises HTTPException: 404 if role not found
    """
    role = await patch_role(user_id, role_patch, db)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role not found for user_id '{user_id}'")
    return role


@router.delete('/role/{user_id}', status_code=204)
async def remove_role_endpoint(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Remove a role for a user
    
    :param user_id: User ID
    :type user_id: str
    :param db: Database session
    :type db: AsyncSession
    :raises HTTPException: 404 if role not found
    """
    success = await remove_role(user_id, db)
    if not success:
        raise HTTPException(status_code=404, detail=f"Role not found for user_id '{user_id}'")
