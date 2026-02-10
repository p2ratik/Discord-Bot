from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.admin import adminRole, adminRoleAdd, adminRolePatch
from app.services.admin_service import get_role_for_admin, add_role_for_admin, patch_role_for_user
from app.db.session import get_db

router = APIRouter(prefix="/api", tags=["admin"])

@router.get('/admin-role/{user_id}', response_model=adminRole)
async def get_admin_role_endpoint(user_id:str, db:AsyncSession = Depends(get_db)):
    """Get admin role for a specific user"""
    admin = await get_role_for_admin(user_id, db)
    if not admin:
        raise HTTPException(status_code=404, detail=f"Admin role not found for user_id '{user_id}'")
    return admin

@router.post('/admin-role', response_model=adminRole, status_code=201)
async def post_admin_role_endpoint(role:adminRoleAdd, db:AsyncSession = Depends(get_db)):
    """Create a new admin role"""
    return await add_role_for_admin(role, db)

@router.patch('/admin-role/{user_id}', response_model=adminRole, status_code=200)
async def patch_admin_role_endpoint(user_id:str, role:adminRolePatch, db:AsyncSession=Depends(get_db)):
    """Update an existing admin role"""
    updated_admin = await patch_role_for_user(user_id, role, db)
    if not updated_admin:
        raise HTTPException(status_code=404, detail=f"Admin role not found for user_id '{user_id}'")
    return updated_admin

