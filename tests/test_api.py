"""E2E tests for the REST API."""
import pytest


@pytest.mark.asyncio(loop_scope="module")
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio(loop_scope="module")
async def test_create_workspace(client):
    resp = await client.post("/api/v1/workspaces", json={"name": "test-team"})
    assert resp.status_code == 200
    data = resp.json()
    assert "workspace_id" in data
    assert "api_key" in data
    assert data["api_key"].startswith("msm_")


@pytest.mark.asyncio(loop_scope="module")
async def test_login(client):
    resp = await client.post("/api/v1/workspaces", json={"name": "login-test"})
    ws_id = resp.json()["workspace_id"]
    resp = await client.post("/api/v1/auth/login", json={
        "workspace_id": ws_id, "user_id": "user-1",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio(loop_scope="module")
async def test_search_requires_auth(client):
    resp = await client.get("/api/v1/workspaces/00000000-0000-0000-0000-000000000001/search?q=test")
    assert resp.status_code == 401
