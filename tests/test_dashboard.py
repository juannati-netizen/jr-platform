from fastapi.testclient import TestClient

from tests.helpers import create_admin_and_login, create_client


def test_dashboard_summary(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    client_id = create_client(client, headers, "Industria Delta")
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
    quote_response = client.post(
        "/api/v1/quotes",
        headers=headers,
        json={
            "client_id": client_id,
            "items": [
                {
                    "description": "Instalación",
                    "quantity": "1.00",
                    "unit_price": "100.00",
                    "tax_rate": "0.00",
                }
            ],
        },
    )
    quote_id = quote_response.json()["id"]
    client.patch(
        f"/api/v1/quotes/{quote_id}",
        headers=headers,
        json={"status": "accepted"},
    )
    invoice = client.post(
        f"/api/v1/quotes/{quote_id}/convert-to-invoice",
        headers=headers,
    ).json()
    client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        headers=headers,
        json={"amount": "40.00", "method": "bank_transfer"},
    )

    response = client.get("/api/v1/dashboard/summary", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["active_clients"] == 1
    assert payload["open_work_orders"] == 1
    assert payload["completed_work_orders"] == 1
    assert payload["unassigned_work_orders"] == 1
    assert payload["accepted_quotes"] == 1
    assert payload["quoted_total"] == "100.00"
    assert payload["invoiced_total"] == "100.00"
    assert payload["collected_total"] == "40.00"
    assert payload["pending_total"] == "60.00"
