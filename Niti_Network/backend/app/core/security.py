from typing import Optional
import httpx
from jose import jwt, JWTError
from app.core.config import settings
from app.core.exceptions import UnauthorizedError

_jwks_cache: Optional[dict] = None


async def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(settings.KEYCLOAK_JWKS_URL, timeout=10)
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache


async def verify_token(token: str) -> dict:
    """
    Decode and validate a Keycloak-issued JWT.
    Returns the decoded payload dict.
    Raises UnauthorizedError on failure.
    """
    try:
        jwks = await _get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.KEYCLOAK_CLIENT_ID,
            issuer=settings.KEYCLOAK_ISSUER,
            options={"verify_exp": True},
        )
        return payload
    except JWTError as exc:
        raise UnauthorizedError(detail=f"Invalid token: {exc}") from exc
    except Exception as exc:
        raise UnauthorizedError(detail=f"Token validation failed: {exc}") from exc


def extract_role(payload: dict) -> str:
    """
    Extract the highest-priority NitiLedger role from the Keycloak token payload.
    Keycloak stores realm roles under: realm_access.roles
    """
    realm_roles = payload.get("realm_access", {}).get("roles", [])
    priority = ["system_admin", "org_admin", "auditor", "contractor", "citizen"]
    for role in priority:
        if role in realm_roles:
            return role
    return "citizen"  # default to most restrictive


def extract_user_id(payload: dict) -> str:
    return payload.get("sub", "unknown")
