from fastapi.testclient import TestClient

from tests.helpers import (
    create_admin_and_login,
    create_client,
    create_supplier,
    register_and_login,
)


def test_admin_can_manage_suppliers(client: TestClient) -> None:
    headers = create_admin_and_login(client)

    created = client.post(
        "/api/v1/suppliers",
        headers=headers,
        json={
            "name": "Suministros Norte",
            "tax_id": "B12345678",
            "email": "compras@suministros.example",
        },
    )
    assert created.status_code == 201
    supplier = created.json()
    assert supplier["name"] == "Suministros Norte"
    assert supplier["tax_id"] == "B12345678"

    listed = client.get("/api/v1/suppliers?active_only=true", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.patch(
        f"/api/v1/suppliers/{supplier['id']}",
        headers=headers,
        json={"is_active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["is_active"] is False


def test_regular_user_cannot_access_procurement(client: TestClient) -> None:
    headers = register_and_login(client)

    assert client.get("/api/v1/suppliers", headers=headers).status_code == 403
    assert client.get("/api/v1/expenses", headers=headers).status_code == 403
    assert client.get("/api/v1/profitability/summary", headers=headers).status_code == 403


def test_expense_totals_filters_and_update(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    supplier_id = create_supplier(client, headers)
    client_id = create_client(client, headers, "Cliente Costes")
    work_order = client.post(
        "/api/v1/work-orders",
        headers=headers,
        json={"client_id": client_id, "title": "Renovar instalación"},
    ).json()

    created = client.post(
        "/api/v1/expenses",
        headers=headers,
        json={
            "supplier_id": supplier_id,
            "work_order_id": work_order["id"],
            "description": "Cableado y protecciones",
            "category": "materials",
            "subtotal": "100.00",
            "tax_rate": "21.00",
            "reference": "ALB-100",
        },
    )
    assert created.status_code == 201
    expense = created.json()
    assert expense["tax_total"] == "21.00"
    assert expense["total"] == "121.00"
    assert expense["supplier"]["name"] == "Proveedor Demo"
    assert expense["work_order"]["client_name"] == "Cliente Costes"

    filtered = client.get("/api/v1/expenses?category=materials", headers=headers)
    assert filtered.status_code == 200
    assert len(filtered.json()) == 1

    updated = client.patch(
        f"/api/v1/expenses/{expense['id']}",
        headers=headers,
        json={"subtotal": "200.00", "status": "paid"},
    )
    assert updated.status_code == 200
    assert updated.json()["total"] == "242.00"
    assert updated.json()["status"] == "paid"


def test_profitability_report_combines_revenue_and_costs(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    supplier_id = create_supplier(client, headers, "Proveedor Rentabilidad")
    client_id = create_client(client, headers, "Cliente Rentable")
    work_order = client.post(
        "/api/v1/work-orders",
        headers=headers,
        json={"client_id": client_id, "title": "Proyecto rentable"},
    ).json()

    invoice = client.post(
        "/api/v1/invoices",
        headers=headers,
        json={
            "client_id": client_id,
            "work_order_id": work_order["id"],
            "items": [
                {
                    "description": "Instalación",
                    "quantity": "1.00",
                    "unit_price": "1000.00",
                    "tax_rate": "0.00",
                }
            ],
        },
    ).json()
    client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        headers=headers,
        json={"amount": "600.00", "method": "bank_transfer"},
    )
    client.post(
        "/api/v1/expenses",
        headers=headers,
        json={
            "supplier_id": supplier_id,
            "work_order_id": work_order["id"],
            "description": "Material",
            "category": "materials",
            "subtotal": "200.00",
            "tax_rate": "0.00",
            "status": "paid",
        },
    )

    response = client.get("/api/v1/profitability/summary", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["invoiced_revenue"] == "1000.00"
    assert payload["collected_revenue"] == "600.00"
    assert payload["expenses_total"] == "200.00"
    assert payload["material_costs"] == "200.00"
    assert payload["gross_margin"] == "800.00"
    assert payload["realized_margin"] == "400.00"
    assert payload["work_orders"][0]["gross_margin"] == "800.00"
    assert payload["clients"][0]["realized_margin"] == "400.00"
