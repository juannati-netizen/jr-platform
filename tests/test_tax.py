from fastapi.testclient import TestClient

from tests.helpers import create_admin_and_login, create_client, register_and_login


def create_invoice_with_igic(client: TestClient, headers: dict[str, str], client_id: str) -> None:
    response = client.post(
        "/api/v1/invoices",
        headers=headers,
        json={
            "client_id": client_id,
            "issue_date": "2026-02-10",
            "items": [
                {
                    "description": "Instalación eléctrica",
                    "quantity": "1.00",
                    "unit_price": "1000.00",
                    "tax_rate": "7.00",
                }
            ],
        },
    )
    assert response.status_code == 201


def create_expense_with_igic(client: TestClient, headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/expenses",
        headers=headers,
        json={
            "description": "Material eléctrico",
            "category": "materials",
            "status": "paid",
            "expense_date": "2026-02-12",
            "subtotal": "200.00",
            "tax_rate": "7.00",
        },
    )
    assert response.status_code == 201


def test_tax_configuration_defaults_to_igic_model_420(client: TestClient) -> None:
    headers = create_admin_and_login(client)

    response = client.get("/api/v1/tax/configuration", headers=headers)

    assert response.status_code == 200
    assert response.json()["tax_system"] == "igic"
    assert response.json()["filing_model"] == "420"
    assert response.json()["filing_frequency"] == "quarterly"
    assert response.json()["default_tax_rate"] == "7.00"


def test_monthly_and_quarterly_igic_summary(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    client_id = create_client(client, headers)
    create_invoice_with_igic(client, headers, client_id)
    create_expense_with_igic(client, headers)

    month = client.get("/api/v1/tax/months/2026/2", headers=headers)
    quarter = client.get("/api/v1/tax/model-420/2026/1", headers=headers)

    assert month.status_code == 200
    assert month.json()["output_base"] == "1000.00"
    assert month.json()["output_tax"] == "70.00"
    assert month.json()["input_base"] == "200.00"
    assert month.json()["input_tax"] == "14.00"
    assert month.json()["result"] == "56.00"
    assert quarter.status_code == 200
    assert quarter.json()["model"] == "420"
    assert quarter.json()["result"] == "56.00"
    assert quarter.json()["filing_window"] == "1–20 de abril de 2026"


def test_manual_adjustment_is_included(client: TestClient) -> None:
    headers = create_admin_and_login(client)

    adjustment = client.post(
        "/api/v1/tax/adjustments",
        headers=headers,
        json={
            "year": 2026,
            "month": 3,
            "direction": "input",
            "amount": "12.50",
            "description": "Regularización de factura recibida",
        },
    )
    month = client.get("/api/v1/tax/months/2026/3", headers=headers)

    assert adjustment.status_code == 201
    assert month.status_code == 200
    assert month.json()["input_adjustments"] == "12.50"
    assert month.json()["result"] == "-12.50"
    assert month.json()["result_type"] == "to_compensate"


def test_closed_month_keeps_snapshot_and_rejects_adjustments(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    client_id = create_client(client, headers)
    create_invoice_with_igic(client, headers, client_id)

    close_response = client.post(
        "/api/v1/tax/months/2026/2/close",
        headers=headers,
        json={"notes": "Revisado"},
    )
    blocked_adjustment = client.post(
        "/api/v1/tax/adjustments",
        headers=headers,
        json={
            "year": 2026,
            "month": 2,
            "direction": "output",
            "amount": "1.00",
            "description": "No debe admitirse",
        },
    )

    assert close_response.status_code == 200
    assert close_response.json()["status"] == "closed"
    assert blocked_adjustment.status_code == 409


def test_regular_user_cannot_access_tax_reporting(client: TestClient) -> None:
    headers = register_and_login(client)

    response = client.get("/api/v1/tax/months?year=2026", headers=headers)

    assert response.status_code == 403
