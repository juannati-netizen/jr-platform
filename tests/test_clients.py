from fastapi.testclient import TestClient

from tests.helpers import register_and_login


def test_client_crud(client: TestClient) -> None:
    headers = register_and_login(client)

    create_response = client.post(
        "/api/v1/clients",
        headers=headers,
        json={
            "name": "Taller Eléctrico Norte",
            "tax_id": "B12345678",
            "email": "contacto@tallernorte.example",
            "phone": "+34 600 000 001",
        },
    )
    assert create_response.status_code == 201
    client_id = create_response.json()["id"]

    list_response = client.get("/api/v1/clients?active_only=true", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        f"/api/v1/clients/{client_id}",
        headers=headers,
        json={"notes": "Cliente prioritario", "is_active": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["notes"] == "Cliente prioritario"
    assert update_response.json()["is_active"] is False


def test_duplicate_tax_id_is_rejected(client: TestClient) -> None:
    headers = register_and_login(client)
    payload = {"name": "Cliente Uno", "tax_id": "A00000001"}
    assert client.post("/api/v1/clients", headers=headers, json=payload).status_code == 201

    duplicate = client.post(
        "/api/v1/clients",
        headers=headers,
        json={"name": "Cliente Dos", "tax_id": "A00000001"},
    )
    assert duplicate.status_code == 409
