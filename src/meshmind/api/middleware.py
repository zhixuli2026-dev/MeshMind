from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

PUBLIC_PATHS = ("/health", "/docs", "/openapi.json")
PUBLIC_POST_PATHS = ("/api/v1/workspaces", "/api/v1/auth/login")


def _extract_token(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return request.query_params.get("token")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in PUBLIC_PATHS or path.startswith("/api/v1/docs"):
            return await call_next(request)

        if request.method == "POST" and any(
            path.startswith(p) for p in PUBLIC_POST_PATHS
        ):
            return await call_next(request)

        token = _extract_token(request)
        if token is None:
            return JSONResponse(
                status_code=401,
                content={"error": {"code": "UNAUTHORIZED", "message": "Missing Bearer token"}},
            )

        request.state.token = token
        request.state.workspace_id = "00000000-0000-0000-0000-000000000001"

        return await call_next(request)
