from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for health check
        if request.url.path in ("/health", "/docs", "/openapi.json"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": {"code": "UNAUTHORIZED", "message": "Missing Bearer token"}},
            )

        token = auth_header[7:]

        # For now: simple token → workspace_id mapping (placeholder)
        # Full JWT/API Key validation will be added in Phase 2
        request.state.token = token
        request.state.workspace_id = _extract_workspace_id(token)

        return await call_next(request)


def _extract_workspace_id(token: str) -> str:
    # Placeholder: return a fixed dev workspace ID for now
    return "00000000-0000-0000-0000-000000000001"
