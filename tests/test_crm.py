from fastapi.testclient import TestClient

from tests.helpers import create_admin_and_login, create_client


def create_lead(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/crm/leads",
        headers=headers,
        json={
            "name": "Ana Pérez",
            "company": "Solar Norte",
            "email": "ana@solarnorte.example",
            "phone": "+34 600 000 001",
            "source": "referral",
            "status": "qualified",
        },
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def test_create_and_convert_lead(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    lead_id = create_lead(client, headers)

    conversion = client.post(
        f"/api/v1/crm/leads/{lead_id}/convert-to-client",
        headers=headers,
    )
    assert conversion.status_code == 200
    assert conversion.json()["name"] == "Solar Norte"

    duplicate = client.post(
        f"/api/v1/crm/leads/{lead_id}/convert-to-client",
        headers=headers,
    )
    assert duplicate.status_code == 409


def test_pipeline_history_and_summary(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    client_id = create_client(client, headers)
    create_response = client.post(
        "/api/v1/crm/opportunities",
        headers=headers,
        json={
            "title": "Instalación fotovoltaica",
            "client_id": client_id,
            "stage": "prospecting",
            "estimated_value": "15000.00",
            "probability": 20,
        },
    )
    assert create_response.status_code == 201
    opportunity_id = create_response.json()["id"]

    move_response = client.patch(
        f"/api/v1/crm/opportunities/{opportunity_id}",
        headers=headers,
        json={"stage": "proposal", "change_source": "kanban"},
    )
    assert move_response.status_code == 200
    assert move_response.json()["stage"] == "proposal"

    history = client.get(
        f"/api/v1/crm/opportunities/{opportunity_id}/stage-history",
        headers=headers,
    )
    assert history.status_code == 200
    assert [item["new_stage"] for item in history.json()] == ["prospecting", "proposal"]

    summary = client.get("/api/v1/crm/summary", headers=headers)
    assert summary.status_code == 200
    assert summary.json()["open_opportunities"] == 1
    assert summary.json()["pipeline_value"] == "15000.00"


def test_opportunity_converts_to_quote_once(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    client_id = create_client(client, headers)
    opportunity = client.post(
        "/api/v1/crm/opportunities",
        headers=headers,
        json={
            "title": "Cuadro eléctrico industrial",
            "client_id": client_id,
            "stage": "proposal",
            "estimated_value": "4500.00",
            "probability": 60,
        },
    ).json()

    conversion = client.post(
        f"/api/v1/crm/opportunities/{opportunity['id']}/convert-to-quote",
        headers=headers,
        json={"tax_rate": "21.00"},
    )
    assert conversion.status_code == 200
    assert conversion.json()["status"] == "draft"
    assert conversion.json()["total"] == "5445.00"

    duplicate = client.post(
        f"/api/v1/crm/opportunities/{opportunity['id']}/convert-to-quote",
        headers=headers,
        json={"tax_rate": "21.00"},
    )
    assert duplicate.status_code == 409


def test_crm_activity_can_be_completed(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    lead_id = create_lead(client, headers)
    response = client.post(
        "/api/v1/crm/activities",
        headers=headers,
        json={
            "lead_id": lead_id,
            "activity_type": "call",
            "subject": "Llamada de seguimiento",
        },
    )
    assert response.status_code == 201
    activity_id = response.json()["id"]

    completion = client.patch(
        f"/api/v1/crm/activities/{activity_id}",
        headers=headers,
        json={"completed": True},
    )
    assert completion.status_code == 200
    assert completion.json()["completed"] is True
    assert completion.json()["completed_at"] is not None
