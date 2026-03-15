from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_token, extract_role, extract_user_id
from app.core.exceptions import UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


class CurrentUser:
    def __init__(self, user_id: str, role: str, payload: dict):
        self.user_id = user_id
        self.role = role
        self.payload = payload


async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """FastAPI dependency — validates JWT and returns the current user."""
    if not token:
        raise UnauthorizedError(detail="Bearer token is missing.")
    payload = await verify_token(token)
    return CurrentUser(
        user_id=extract_user_id(payload),
        role=extract_role(payload),
        payload=payload,
    )
