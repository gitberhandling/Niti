from typing import Optional
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import settings
from app.core.exceptions import UnauthorizedError

router = APIRouter(prefix="/auth", tags=["Authentication"])


class TokenRequest(BaseModel):
    code: str
    redirect_uri: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None


@router.post("/token", response_model=TokenResponse, summary="Exchange Keycloak OIDC code for JWT")
async def get_token(body: TokenRequest):
    """
    Exchange a Keycloak OIDC authorization code for a JWT access token.
    This is a public endpoint — no auth required.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            settings.KEYCLOAK_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": settings.KEYCLOAK_CLIENT_ID,
                "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
                "code": body.code,
                "redirect_uri": body.redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15,
        )

    if resp.status_code != 200:
        raise UnauthorizedError(detail=f"Keycloak rejected the token exchange: {resp.text}")

    data = resp.json()
    return TokenResponse(
        access_token=data["access_token"],
        token_type=data.get("token_type", "bearer"),
        expires_in=data.get("expires_in", 3600),
        refresh_token=data.get("refresh_token"),
    )
