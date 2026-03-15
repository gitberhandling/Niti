"""
Hyperledger Fabric Gateway Client (Sprint 1 stub).
Full implementation in Sprint 2 using fabric-gateway Python SDK.
In development mode (APP_ENV=development) this returns a mock TX ID.
"""
import uuid
from typing import List
from app.core.config import settings
from app.core.exceptions import BlockchainError


class FabricClient:
    """Thin wrapper around the Hyperledger Fabric Gateway."""

    async def invoke_chaincode(self, function_name: str, args: List[str]) -> str:
        """
        Invoke a chaincode transaction (submit).
        Returns transaction ID.
        """
        if settings.APP_ENV == "development":
            # Dev stub — returns a deterministic fake TX ID
            return f"dev-txid-{function_name.lower()}-{str(uuid.uuid4())[:8]}"
        # TODO Sprint 2: connect to real Fabric peer via grpc
        raise BlockchainError("Fabric peer not configured for production yet.")

    async def query_chaincode(self, function_name: str, args: List[str]) -> dict:
        """
        Query chaincode (evaluate — read-only, no endorsement).
        Returns parsed JSON response.
        """
        if settings.APP_ENV == "development":
            return {"stub": True, "function": function_name, "args": args}
        raise BlockchainError("Fabric peer not configured for production yet.")
