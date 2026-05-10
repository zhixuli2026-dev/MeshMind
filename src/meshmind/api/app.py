from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from meshmind.api.deps import init_services
from meshmind.api.middleware import AuthMiddleware
from meshmind.embedding.encoder import EmbeddingEncoder


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.encoder = EmbeddingEncoder()
    init_services()
    yield
    app.state.encoder = None


app = FastAPI(
    title="MeshMind",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


from meshmind.api.routes import (
    auth, documents, extract, members, nodes, relations, search, workspaces,
)
from meshmind.api.sse import agent as sse_agent, task as sse_task

routers = [search, nodes, extract, workspaces, auth, members, relations, documents]
for r in routers:
    app.include_router(r.router, prefix="/api/v1")

from meshmind.mcp.server import create_mcp_server

app.include_router(sse_agent.router, prefix="/api/v1")
app.include_router(sse_task.router, prefix="/api/v1")

mcp = create_mcp_server()


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
