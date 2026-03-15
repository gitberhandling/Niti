from typing import List
from fastapi import Depends
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.core.exceptions import InsufficientRoleError


def require_roles(*allowed_roles: str):
    """
    Factory that returns a FastAPI dependency enforcing role-based access control.
    Usage:
        @router.post("/projects", dependencies=[Depends(require_roles("org_admin", "system_admin"))])
    """
    allowed = set(allowed_roles)

    async def check_role(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed:
            raise InsufficientRoleError()
        return current_user

    return check_role
