import pytest
from sqlalchemy.pool import StaticPool

from app import create_app
from app.config import Config


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
    JWT_SECRET = "test-secret-0123456789abcdef0123456789"


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as c:
        yield c


def get_token(client, username="admin", password="CorrectHorse42!"):
    resp = client.post("/auth/login", json={"username": username, "password": password})
    return resp.get_json()["token"]


def test_login_success(client):
    resp = client.post(
        "/auth/login", json={"username": "admin", "password": "CorrectHorse42!"}
    )
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_login_wrong_password(client):
    resp = client.post(
        "/auth/login", json={"username": "admin", "password": "nope"}
    )
    assert resp.status_code == 401


def test_sqli_payload_is_rejected(client):
    resp = client.post(
        "/auth/login", json={"username": "admin' OR '1'='1", "password": "x"}
    )
    assert resp.status_code == 401


def test_data_requires_auth(client):
    assert client.get("/api/data").status_code == 401


def test_data_with_token(client):
    token = get_token(client)
    resp = client.get("/api/data", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "crystals" in resp.get_json()


def test_xss_username_is_escaped(client):
    client.post(
        "/auth/register",
        json={"username": "<script>alert(1)</script>", "password": "password123"},
    )
    token = get_token(client, "<script>alert(1)</script>", "password123")
    resp = client.get("/api/data", headers={"Authorization": f"Bearer {token}"})
    assert "<script>" not in resp.get_json()["user"]
    assert "&lt;script&gt;" in resp.get_json()["user"]


def test_buy_reduces_balance_and_stock(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post(
        "/api/buy", json={"crystal_id": 1, "quantity": 2}, headers=headers
    )
    assert resp.status_code == 201
    assert resp.get_json()["quantity"] == 2
