from fastapi.testclient import TestClient

from tests.helpers import register_and_login


def test_dashboard_summary(client: TestClient) -> None:
    headers = register_and_login(client)
    client_response = client.post(
        "/api/v1/clients",
        headers=headers,
        json={"name": "Industria Delta"},
    )
    client_id = client_response.json()["id"]
    client.post(
        "/api/v1/work-orders",
        headers=headers,
        json={"client_id": client_id, "title": "Instalar línea", "status": "in_progress"},
    )
    client.post(
        "/api/v1/work-orders",
        headers=headers,
        json={"client_id": client_id, "title": "Revisar luminarias", "status": "completed"},
    )

    response = client.get("/api/v1/dashboard/summary", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["active_clients"] == 1
    assert payload["open_work_orders"] == 1
    assert payload["completed_work_orders"] == 1
    assert payload["unassigned_work_orders"] == 1
