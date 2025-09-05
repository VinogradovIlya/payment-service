import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """FastAPI тест клиент"""
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """Уникальные данные тестового пользователя"""
    import uuid

    unique_id = str(uuid.uuid4())[:8]

    return {
        "email": f"test{unique_id}@example.com",
        "username": f"testuser{unique_id}",
        "password": "password123",
        "full_name": "Test User",
    }


@pytest.fixture
def second_test_user_data():
    """Уникальные данные второго тестового пользователя"""
    import uuid

    unique_id = str(uuid.uuid4())[:8]

    return {
        "email": f"user2{unique_id}@example.com",
        "username": f"testuser2{unique_id}",
        "password": "password123",
        "full_name": "Test User 2",
    }


@pytest.fixture
def authenticated_user(client: TestClient, test_user_data: dict):
    """Создает аутентифицированного пользователя"""
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 200

    token = response.json()["access_token"]
    user_info = response.json()["user"]

    return {
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "user": user_info,
        "data": test_user_data,
    }


@pytest.fixture
def second_user(client: TestClient, second_test_user_data: dict):
    """Создает второго аутентифицированного пользователя"""
    response = client.post("/auth/register", json=second_test_user_data)
    assert response.status_code == 200

    token = response.json()["access_token"]
    user_info = response.json()["user"]

    return {
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "user": user_info,
        "data": second_test_user_data,
    }
