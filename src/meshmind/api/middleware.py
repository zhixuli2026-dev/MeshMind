from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

PUBLIC_PATHS = ("/health", "/docs", "/openapi.json")
PUBLIC_POST_PATHS = ("/api/v1/workspaces", "/api/v1/auth/login")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in PUBLIC_PATHS:
            return await call_next(request)

        if request.method == "POST" and any(
            path.startswith(p) for p in PUBLIC_POST_PATHS
        ):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": {"code": "UNAUTHORIZED", "message": "Missing Bearer token"}},
            )

        token = auth_header[7:]
        request.state.token = token
        request.state.workspace_id = "00000000-0000-0000-0000-000000000001"

        return await call_next(request)
