from pydantic import BaseModel
from typing import Optional


class RoleCreate(BaseModel):
    """Pydantic schema for creating a Role"""
    user_id: str
    user_name: str
    role: dict


class RolePatch(BaseModel):
    """Pydantic schema for partially updating a Role"""
    role: dict


class Role(BaseModel):
    """Pydantic schema for Role"""
    id: int
    user_id: str
    user_name: str
    role: dict

