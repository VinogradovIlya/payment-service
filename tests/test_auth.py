import pytest
from fastapi.testclient import TestClient


class TestAuth:
    """Тесты аутентификации"""

    def test_register_user_success(self, client: TestClient, test_user_data: dict):
        """Тест успешной регистрации пользователя"""
        response = client.post("/auth/register", json=test_user_data)

        assert response.status_code == 200
        data = response.json()

        # Проверяем токен
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 10

        # Проверяем пользователя
        user = data["user"]
        assert user["email"] == test_user_data["email"]
        assert user["username"] == test_user_data["username"]
        assert user["full_name"] == test_user_data["full_name"]
        assert user["balance"] == "1000.00"
        assert "id" in user
        assert "created_at" in user

    def test_register_duplicate_username(self, client: TestClient, test_user_data: dict):
        """Тест регистрации с существующим username"""
        # Первая регистрация
        response1 = client.post("/auth/register", json=test_user_data)
        assert response1.status_code == 200

        # Попытка с тем же username, но другим email
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = "another@example.com"

        response2 = client.post("/auth/register", json=duplicate_data)
        assert response2.status_code == 400
        error_detail = response2.json()["detail"]
        assert "username уже существует" in error_detail

    def test_register_duplicate_email(self, client: TestClient, test_user_data: dict):
        """Тест регистрации с существующим email"""
        # Первая регистрация
        response1 = client.post("/auth/register", json=test_user_data)
        assert response1.status_code == 200

        # Попытка с тем же email, но другим username
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "anotheruser"

        response2 = client.post("/auth/register", json=duplicate_data)
        assert response2.status_code == 400
        error_detail = response2.json()["detail"]
        assert "email уже существует" in error_detail

    def test_login_success(self, client: TestClient, test_user_data: dict):
        """Тест успешного входа"""
        # Регистрация
        client.post("/auth/register", json=test_user_data)

        # Вход
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }

        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    def test_login_wrong_password(self, client: TestClient, test_user_data: dict):
        """Тест входа с неправильным паролем"""
        # Регистрация
        client.post("/auth/register", json=test_user_data)

        # Вход с неправильным паролем
        login_data = {"username": test_user_data["username"], "password": "wrongpassword"}

        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Неверные учетные данные" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Тест входа несуществующего пользователя"""
        login_data = {"username": "nonexistent", "password": "password123"}

        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401

    def test_get_current_user_success(self, client: TestClient, authenticated_user: dict):
        """Тест получения информации о текущем пользователе"""
        response = client.get("/auth/me", headers=authenticated_user["headers"])

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == authenticated_user["data"]["email"]
        assert data["username"] == authenticated_user["data"]["username"]
        assert data["balance"] == "1000.00"

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Тест получения информации с невалидным токеном"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 401

    def test_get_current_user_no_token(self, client: TestClient):
        """Тест получения информации без токена"""
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_register_invalid_email(self, client: TestClient):
        """Тест регистрации с невалидным email"""
        invalid_data = {
            "email": "not-an-email",
            "username": "testuser",
            "password": "password123",
            "full_name": "Test User",
        }

        response = client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422

    def test_register_short_username(self, client: TestClient):
        """Тест регистрации с коротким username"""
        invalid_data = {
            "email": "test@example.com",
            "username": "ab",  # Меньше 3 символов
            "password": "password123",
            "full_name": "Test User",
        }

        response = client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422

    def test_register_short_password(self, client: TestClient):
        """Тест регистрации с коротким паролем"""
        invalid_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "123",  # Меньше 6 символов
            "full_name": "Test User",
        }

        response = client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422

    def test_multiple_users_registration(self, client: TestClient):
        """Тест регистрации нескольких пользователей"""
        users = [
            {
                "email": "user1@example.com",
                "username": "user1",
                "password": "password123",
                "full_name": "User One",
            },
            {
                "email": "user2@example.com",
                "username": "user2",
                "password": "password456",
                "full_name": "User Two",
            },
        ]

        for i, user_data in enumerate(users):
            response = client.post("/auth/register", json=user_data)
            assert response.status_code == 200

            # Проверяем уникальность данных
            data = response.json()
            assert data["user"]["username"] == user_data["username"]
            assert data["user"]["email"] == user_data["email"]
