from fastapi.testclient import TestClient

from tests.helpers import register_and_login


def create_client(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        headers=headers,
        json={"name": "Comunidad Sol", "email": "gestion@comunidadsol.example"},
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def test_work_order_lifecycle_and_notes(client: TestClient) -> None:
    headers = register_and_login(client)
    client_id = create_client(client, headers)

    create_response = client.post(
        "/api/v1/work-orders",
        headers=headers,
        json={
            "client_id": client_id,
            "title": "Revisar cuadro general",
            "description": "Comprobar protecciones y aprietes.",
            "status": "planned",
            "priority": "high",
        },
    )
    assert create_response.status_code == 201
    work_order_id = create_response.json()["id"]
    assert create_response.json()["client"]["name"] == "Comunidad Sol"

    note_response = client.post(
        f"/api/v1/work-orders/{work_order_id}/notes",
        headers=headers,
        json={"content": "Acceso confirmado con el presidente."},
    )
    assert note_response.status_code == 201

    update_response = client.patch(
        f"/api/v1/work-orders/{work_order_id}",
        headers=headers,
        json={"status": "completed"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "completed"
    assert update_response.json()["completed_at"] is not None
    assert update_response.json()["notes_count"] == 1

    notes_response = client.get(
        f"/api/v1/work-orders/{work_order_id}/notes",
        headers=headers,
    )
    assert notes_response.status_code == 200
    assert notes_response.json()[0]["content"].startswith("Acceso confirmado")


def test_work_order_requires_existing_client(client: TestClient) -> None:
    headers = register_and_login(client)
    response = client.post(
        "/api/v1/work-orders",
        headers=headers,
        json={"client_id": "missing", "title": "Trabajo imposible"},
    )
    assert response.status_code == 422
