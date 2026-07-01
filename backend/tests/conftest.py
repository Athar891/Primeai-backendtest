import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base import Base
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield session_factory

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_token(client):
    await client.post("/api/v1/auth/register", json={"email": "admin@example.com", "password": "adminpass123"})
    resp = await client.post(
        "/api/v1/auth/login", data={"username": "admin@example.com", "password": "adminpass123"}
    )
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def user_token(client):
    await client.post("/api/v1/auth/register", json={"email": "jane@example.com", "password": "janepass123"})
    resp = await client.post(
        "/api/v1/auth/login", data={"username": "jane@example.com", "password": "janepass123"}
    )
    return resp.json()["access_token"]
