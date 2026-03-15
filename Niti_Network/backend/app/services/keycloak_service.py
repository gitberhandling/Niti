import httpx
from app.core.config import settings


class KeycloakService:
    """Interact with Keycloak admin API for user management."""

    async def get_user_info(self, access_token: str) -> dict:
        """Fetch user info from Keycloak's userinfo endpoint."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.KEYCLOAK_ISSUER}/protocol/openid-connect/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()

    async def refresh_jwks(self) -> dict:
        """Force-refresh the JWKS cache from Keycloak."""
        from app.core import security
        security._jwks_cache = None
        return await security._get_jwks()
