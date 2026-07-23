from fastapi.testclient import TestClient

USER_PAYLOAD = {
    "email": "user@example.com",
    "full_name": "Usuario Prueba",
    "password": "SecurePass123!",
}


def test_register_login_and_read_profile(client: TestClient) -> None:
    register_response = client.post("/api/v1/auth/register", json=USER_PAYLOAD)

    assert register_response.status_code == 201
    assert register_response.json()["email"] == USER_PAYLOAD["email"]
    assert register_response.json()["role"] == "user"
    assert "hashed_password" not in register_response.json()

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": USER_PAYLOAD["email"],
            "password": USER_PAYLOAD["password"],
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    profile_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == USER_PAYLOAD["email"]


def test_duplicate_registration_is_rejected(client: TestClient) -> None:
    assert client.post("/api/v1/auth/register", json=USER_PAYLOAD).status_code == 201

    duplicate_response = client.post("/api/v1/auth/register", json=USER_PAYLOAD)

    assert duplicate_response.status_code == 409


def test_invalid_login_is_rejected(client: TestClient) -> None:
    client.post("/api/v1/auth/register", json=USER_PAYLOAD)

    response = client.post(
        "/api/v1/auth/login",
        data={"username": USER_PAYLOAD["email"], "password": "incorrecta"},
    )

    assert response.status_code == 401
