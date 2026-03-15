from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request


class NitiException(Exception):
    """Base NitiLedger application exception."""

    def __init__(self, error: str, detail: str, status_code: int = 400):
        self.error = error
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundError(NitiException):
    def __init__(self, resource: str, id: str):
        super().__init__(
            error="not_found",
            detail=f"{resource} with id '{id}' was not found.",
            status_code=404,
        )


class UnauthorizedError(NitiException):
    def __init__(self, detail: str = "Authentication required."):
        super().__init__(error="unauthorized", detail=detail, status_code=401)


class InsufficientRoleError(NitiException):
    def __init__(self):
        super().__init__(
            error="insufficient_role",
            detail="You do not have permission to perform this action.",
            status_code=403,
        )


class ValidationError(NitiException):
    def __init__(self, detail: str):
        super().__init__(error="validation_error", detail=detail, status_code=422)


class BlockchainError(NitiException):
    def __init__(self, detail: str):
        super().__init__(error="blockchain_error", detail=detail, status_code=502)


class HashMismatchError(NitiException):
    def __init__(self, document_id: str):
        super().__init__(
            error="hash_mismatch",
            detail=f"Document '{document_id}' hash does not match on-chain record.",
            status_code=409,
        )


async def niti_exception_handler(request: Request, exc: NitiException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error, "detail": exc.detail},
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "http_error", "detail": exc.detail},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "detail": "An unexpected error occurred."},
    )
