from pydantic import BaseModel

class adminRole(BaseModel):
    id : int
    user_id : str
    role : dict

class adminRoleAdd(BaseModel):
    user_id : str
    role : dict

class adminRolePatch(BaseModel):
    role : dict
