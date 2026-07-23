from fastapi.testclient import TestClient

from apps.db.session import SessionLocal
from apps.models.user import UserRole
from apps.repositories.users import create_user
from apps.schemas.user import UserCreate


def create_admin() -> None:
    with SessionLocal() as db:
        create_user(
            db,
            UserCreate(
                email="admin@example.com",
                full_name="Administrador",
                password="AdminPass123!",
            ),
            role=UserRole.ADMIN,
        )


def login(client: TestClient, email: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_regular_user_cannot_list_users(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "full_name": "Usuario",
            "password": "SecurePass123!",
        },
    )
    token = login(client, "user@example.com", "SecurePass123!")

    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_admin_can_list_users_and_change_role(client: TestClient) -> None:
    create_admin()
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "full_name": "Usuario",
            "password": "SecurePass123!",
        },
    )
    user_id = register_response.json()["id"]
    admin_token = login(client, "admin@example.com", "AdminPass123!")
    headers = {"Authorization": f"Bearer {admin_token}"}

    list_response = client.get("/api/v1/users", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2

    role_response = client.patch(
        f"/api/v1/users/{user_id}/role",
        json={"role": "admin"},
        headers=headers,
    )

    assert role_response.status_code == 200
    assert role_response.json()["role"] == "admin"
