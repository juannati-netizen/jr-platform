from fastapi.testclient import TestClient

from tests.helpers import create_admin_and_login, create_client, register_and_login

ITEMS = [
    {
        "description": "Instalación de cuadro eléctrico",
        "quantity": "2.00",
        "unit_price": "100.00",
        "tax_rate": "21.00",
    },
    {
        "description": "Material auxiliar",
        "quantity": "1.00",
        "unit_price": "50.00",
        "tax_rate": "10.00",
    },
]


def create_quote(
    client: TestClient,
    headers: dict[str, str],
    client_id: str,
) -> dict[str, object]:
    response = client.post(
        "/api/v1/quotes",
        headers=headers,
        json={
            "client_id": client_id,
            "valid_until": "2026-08-31",
            "notes": "Incluye desplazamiento.",
            "items": ITEMS,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_quote_totals_and_status_lifecycle(client: TestClient) -> None:
    headers = register_and_login(client)
    client_id = create_client(client, headers)

    quote = create_quote(client, headers, client_id)
    assert str(quote["number"]).startswith("PRE-")
    assert quote["subtotal"] == "250.00"
    assert quote["tax_total"] == "47.00"
    assert quote["total"] == "297.00"
    assert quote["status"] == "draft"

    sent = client.patch(
        f"/api/v1/quotes/{quote['id']}",
        headers=headers,
        json={"status": "sent"},
    )
    assert sent.status_code == 200
    assert sent.json()["status"] == "sent"

    listed = client.get("/api/v1/quotes?status=sent", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_accepted_quote_conversion_and_payments(client: TestClient) -> None:
    admin_headers = create_admin_and_login(client)
    client_id = create_client(client, admin_headers, "Industria Financiera")
    quote = create_quote(client, admin_headers, client_id)

    accepted = client.patch(
        f"/api/v1/quotes/{quote['id']}",
        headers=admin_headers,
        json={"status": "accepted"},
    )
    assert accepted.status_code == 200

    converted = client.post(
        f"/api/v1/quotes/{quote['id']}/convert-to-invoice?due_date=2026-09-15",
        headers=admin_headers,
    )
    assert converted.status_code == 200
    invoice = converted.json()
    assert str(invoice["number"]).startswith("FAC-")
    assert invoice["source_quote_id"] == quote["id"]
    assert invoice["pending_total"] == "297.00"

    partial = client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        headers=admin_headers,
        json={"amount": "100.00", "method": "bank_transfer", "reference": "TRX-1"},
    )
    assert partial.status_code == 200
    assert partial.json()["status"] == "partial"
    assert partial.json()["paid_total"] == "100.00"
    assert partial.json()["pending_total"] == "197.00"

    paid = client.post(
        f"/api/v1/invoices/{invoice['id']}/payments",
        headers=admin_headers,
        json={"amount": "197.00", "method": "card"},
    )
    assert paid.status_code == 200
    assert paid.json()["status"] == "paid"
    assert paid.json()["pending_total"] == "0.00"
    assert len(paid.json()["payments"]) == 2


def test_regular_user_cannot_create_invoice_or_convert_quote(client: TestClient) -> None:
    headers = register_and_login(client)
    client_id = create_client(client, headers)
    quote = create_quote(client, headers, client_id)
    client.patch(
        f"/api/v1/quotes/{quote['id']}",
        headers=headers,
        json={"status": "accepted"},
    )

    conversion = client.post(
        f"/api/v1/quotes/{quote['id']}/convert-to-invoice",
        headers=headers,
    )
    assert conversion.status_code == 403

    direct_invoice = client.post(
        "/api/v1/invoices",
        headers=headers,
        json={"client_id": client_id, "items": ITEMS},
    )
    assert direct_invoice.status_code == 403


def test_payment_cannot_exceed_pending_total(client: TestClient) -> None:
    admin_headers = create_admin_and_login(client)
    client_id = create_client(client, admin_headers)
    response = client.post(
        "/api/v1/invoices",
        headers=admin_headers,
        json={
            "client_id": client_id,
            "items": [
                {
                    "description": "Servicio",
                    "quantity": "1.00",
                    "unit_price": "100.00",
                    "tax_rate": "0.00",
                }
            ],
        },
    )
    invoice_id = response.json()["id"]

    overpayment = client.post(
        f"/api/v1/invoices/{invoice_id}/payments",
        headers=admin_headers,
        json={"amount": "101.00", "method": "cash"},
    )
    assert overpayment.status_code == 422
