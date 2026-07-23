from fastapi.testclient import TestClient

from apps.db.session import SessionLocal
from apps.models.user import UserRole
from apps.repositories.users import create_user
from apps.schemas.user import UserCreate


def login(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def register_and_login(
    client: TestClient,
    *,
    email: str = "operator@example.com",
    full_name: str = "Operador Prueba",
) -> dict[str, str]:
    password = "SecurePass123!"
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": full_name, "password": password},
    )
    assert register_response.status_code == 201
    return login(client, email, password)


def create_admin_and_login(client: TestClient) -> dict[str, str]:
    with SessionLocal() as db:
        create_user(
            db,
            UserCreate(
                email="admin@example.com",
                full_name="Administrador Prueba",
                password="AdminPass123!",
            ),
            role=UserRole.ADMIN,
        )
    return login(client, "admin@example.com", "AdminPass123!")


def create_client(client: TestClient, headers: dict[str, str], name: str = "Cliente Demo") -> str:
    response = client.post(
        "/api/v1/clients",
        headers=headers,
        json={"name": name, "email": "cliente@example.com"},
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def create_supplier(
    client: TestClient,
    headers: dict[str, str],
    name: str = "Proveedor Demo",
) -> str:
    response = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={"name": name, "email": "proveedor@example.com"},
    )
    assert response.status_code == 201
    return str(response.json()["id"])
