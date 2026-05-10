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


from meshmind.api.routes import search, nodes, extract

app.include_router(search.router)
app.include_router(nodes.router)
app.include_router(extract.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
