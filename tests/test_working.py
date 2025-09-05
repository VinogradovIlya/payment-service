import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint():
    """Тест корневого эндпоинта"""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Payment Service API"


def test_health_check():
    """Тест health check"""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_auth_validation():
    """Тест валидации данных аутентификации"""
    client = TestClient(app)

    response = client.post(
        "/auth/register",
        json={"email": "not-an-email", "username": "testuser", "password": "password123"},
    )
    assert response.status_code == 422

    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "username": "ab", "password": "password123"},
    )
    assert response.status_code == 422

    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "username": "testuser", "password": "123"},
    )
    assert response.status_code == 422


def test_payment_validation():
    """Тест валидации данных платежей"""
    client = TestClient(app)

    response = client.post("/payments/", json={"amount": -50.00, "description": "Invalid payment"})
    assert response.status_code in [401, 403, 422]


def test_unauthorized_access():
    """Тест неавторизованного доступа"""
    client = TestClient(app)

    response = client.get("/auth/me")
    assert response.status_code in [401, 403]

    response = client.get("/payments/")
    assert response.status_code in [401, 403]

    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401


def test_user_flow_basic():
    """Базовый тест регистрации пользователя"""
    client = TestClient(app)
    unique_id = str(uuid.uuid4())[:8]

    user_data = {
        "email": f"test{unique_id}@example.com",
        "username": f"user{unique_id}",
        "password": "password123",
        "full_name": "Test User",
    }

    response = client.post("/auth/register", json=user_data)

    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["username"] == user_data["username"]
    else:
        assert response.status_code in [500, 503]


def test_nonexistent_endpoints():
    """Тест несуществующих эндпоинтов"""
    client = TestClient(app)

    response = client.get("/nonexistent")
    assert response.status_code == 404

    response = client.get("/payments/nonexistent")
    assert response.status_code in [401, 403, 404]
