import pytest


async def test_register_success(client):
    resp = await client.post("/api/v1/auth/register", json={"email": "new@example.com", "password": "password123"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert data["role"] == "user"
    assert "hashed_password" not in data


async def test_register_admin_email_gets_admin_role(client):
    resp = await client.post("/api/v1/auth/register", json={"email": "admin@example.com", "password": "adminpass123"})
    assert resp.status_code == 201
    assert resp.json()["role"] == "admin"


async def test_register_duplicate_email_returns_409(client):
    await client.post("/api/v1/auth/register", json={"email": "dupe@example.com", "password": "password123"})
    resp = await client.post("/api/v1/auth/register", json={"email": "dupe@example.com", "password": "password123"})
    assert resp.status_code == 409


async def test_register_invalid_email_returns_422(client):
    resp = await client.post("/api/v1/auth/register", json={"email": "not-an-email", "password": "password123"})
    assert resp.status_code == 422


async def test_register_short_password_returns_422(client):
    resp = await client.post("/api/v1/auth/register", json={"email": "short@example.com", "password": "short"})
    assert resp.status_code == 422


async def test_login_success(client):
    await client.post("/api/v1/auth/register", json={"email": "jane@example.com", "password": "janepass123"})
    resp = await client.post("/api/v1/auth/login", data={"username": "jane@example.com", "password": "janepass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_login_wrong_password_returns_401(client):
    await client.post("/api/v1/auth/register", json={"email": "jane@example.com", "password": "janepass123"})
    resp = await client.post("/api/v1/auth/login", data={"username": "jane@example.com", "password": "wrongpass"})
    assert resp.status_code == 401


async def test_login_unknown_user_returns_401(client):
    resp = await client.post("/api/v1/auth/login", data={"username": "ghost@example.com", "password": "whatever"})
    assert resp.status_code == 401


async def test_me_without_token_returns_401(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_me_with_invalid_token_returns_401(client):
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer garbage.token.value"})
    assert resp.status_code == 401


async def test_me_with_valid_token_returns_user(client, user_token):
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "jane@example.com"
