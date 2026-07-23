from fastapi.testclient import TestClient


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
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == 200
    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}
