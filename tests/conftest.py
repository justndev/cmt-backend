import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_database():
    Base.metadata.create_all(bind=engine)
    yield
    os.remove("./test.db")

# Weird error discovered. Two functions where one has extra unused prop of fixture will always receive 422...

# v1 will be successful
#def test_create_provider_v1(client):
#     response = client.post("/api/cmt/providers", json={"name": "TestProvider"})
#     assert response.status_code in (200, 201, 400)
#     if response.status_code == 200:
#         assert response.json()["name"] == "TestProvider"

# v2 will receive 422, even if test_user prop is unused.
# def test_create_provider_v2(client, test_user):
#     response = client.post("/api/cmt/providers", json={"name": "TestProvider"})
#     assert response.status_code in (200, 201, 400)
#     if response.status_code == 200:
#         assert response.json()["name"] == "TestProvider"



@pytest.fixture(scope="session")
def client():
    return TestClient(app)