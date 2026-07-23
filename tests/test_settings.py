from fastapi.testclient import TestClient

from tests.helpers import create_admin_and_login, register_and_login


def company_payload() -> dict[str, object]:
    return {
        "legal_name": "JR Electricidad SL",
        "trade_name": "JR Energy",
        "tax_id": "B12345678",
        "legal_form": "Sociedad limitada",
        "tax_regime": "Régimen general",
        "address": "Calle Instaladores 10",
        "postal_code": "28001",
        "city": "Madrid",
        "province": "Madrid",
        "country": "España",
        "email": "administracion@jrenergy.example",
        "phone": "600000000",
        "website": "https://jrenergy.example",
        "iban": "ES0000000000000000000000",
        "invoice_prefix": "F",
        "quote_prefix": "P",
        "currency": "EUR",
        "timezone": "Europe/Madrid",
        "logo_data_url": None,
        "brand_color": "#005bbb",
        "document_footer": "Gracias por confiar en JR Energy",
    }


def test_admin_can_save_company_profile(client: TestClient) -> None:
    headers = create_admin_and_login(client)

    response = client.put("/api/v1/settings/company", headers=headers, json=company_payload())

    assert response.status_code == 200
    assert response.json()["legal_name"] == "JR Electricidad SL"
    assert response.json()["trade_name"] == "JR Energy"


def test_regular_user_cannot_read_company_settings(client: TestClient) -> None:
    headers = register_and_login(client)

    response = client.get("/api/v1/settings/company", headers=headers)

    assert response.status_code == 403


def test_admin_can_open_close_and_reopen_fiscal_year(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    create_response = client.post(
        "/api/v1/settings/fiscal-years",
        headers=headers,
        json={
            "year": 2026,
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "notes": "Ejercicio inicial",
        },
    )
    assert create_response.status_code == 201
    fiscal_year_id = create_response.json()["id"]
    assert create_response.json()["status"] == "open"

    close_response = client.post(
        f"/api/v1/settings/fiscal-years/{fiscal_year_id}/close",
        headers=headers,
    )
    assert close_response.status_code == 200
    assert close_response.json()["status"] == "closed"

    reopen_response = client.post(
        f"/api/v1/settings/fiscal-years/{fiscal_year_id}/open",
        headers=headers,
    )
    assert reopen_response.status_code == 200
    assert reopen_response.json()["status"] == "open"


def test_duplicate_fiscal_year_is_rejected(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    payload = {
        "year": 2026,
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
    }

    first = client.post("/api/v1/settings/fiscal-years", headers=headers, json=payload)
    second = client.post("/api/v1/settings/fiscal-years", headers=headers, json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_verifactu_readiness_is_explicitly_not_a_certification(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    client.put("/api/v1/settings/company", headers=headers, json=company_payload())
    client.put(
        "/api/v1/settings/verifactu",
        headers=headers,
        json={
            "mode": "preparation",
            "system_name": "JR Platform",
            "system_version": "0.11.0",
            "producer_name": "JR Platform",
            "producer_tax_id": "B12345678",
            "qr_enabled": True,
            "hash_chain_enabled": True,
            "event_log_enabled": True,
            "aeat_transmission_enabled": False,
            "responsible_declaration_signed": False,
            "certificate_alias": None,
            "notes": "Preparación interna",
        },
    )

    response = client.get("/api/v1/settings/verifactu/readiness", headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    assert response.json()["transmission_active"] is False
    assert "No certifica" in response.json()["legal_notice"]


def test_ai_configuration_never_exposes_secret(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    response = client.put(
        "/api/v1/settings/ai",
        headers=headers,
        json={
            "enabled": False,
            "provider": "openai",
            "model": "gpt-example",
            "assistant_name": "Asistente JR",
            "system_prompt": "Ayuda con tareas administrativas.",
            "allow_customer_data": False,
            "allow_financial_data": False,
            "allow_document_content": False,
            "human_review_required": True,
            "retention_days": 0,
            "notes": None,
        },
    )

    assert response.status_code == 200
    assert "api_key" not in response.json()
    assert response.json()["api_key_configured"] is False


def test_admin_can_save_company_logo(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    payload = company_payload()
    payload["logo_data_url"] = "data:image/png;base64,aGVsbG8="

    response = client.put("/api/v1/settings/company", headers=headers, json=payload)
    public_response = client.get("/api/v1/settings/company/public", headers=headers)

    assert response.status_code == 200
    assert response.json()["logo_data_url"].startswith("data:image/png;base64,")
    assert public_response.status_code == 200
    assert public_response.json()["brand_color"] == "#005bbb"


def test_invalid_company_logo_is_rejected(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    payload = company_payload()
    payload["logo_data_url"] = "data:image/svg+xml;base64,PHN2Zz4="

    response = client.put("/api/v1/settings/company", headers=headers, json=payload)

    assert response.status_code == 422


def test_authenticated_user_can_read_public_company_identity(client: TestClient) -> None:
    admin_headers = create_admin_and_login(client)
    client.put("/api/v1/settings/company", headers=admin_headers, json=company_payload())
    user_headers = register_and_login(client)

    response = client.get("/api/v1/settings/company/public", headers=user_headers)

    assert response.status_code == 200
    assert response.json()["trade_name"] == "JR Energy"
    assert "iban" not in response.json()
