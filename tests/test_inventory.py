from pathlib import Path

from fastapi.testclient import TestClient

from apps.core.config import settings
from tests.helpers import create_admin_and_login, create_client, register_and_login


def create_catalog_item(client: TestClient, headers: dict[str, str]) -> dict[str, object]:
    response = client.post(
        "/api/v1/catalog",
        headers=headers,
        json={
            "code": "MAT-CABLE-25",
            "family": "Cableado",
            "description": "Cable manguera 3G2,5 mm²",
            "unit": "m",
            "purchase_price": "2.00",
            "sale_price": "4.50",
            "tax_rate": "7.00",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_warehouse(client: TestClient, headers: dict[str, str]) -> dict[str, object]:
    response = client.post(
        "/api/v1/warehouses",
        headers=headers,
        json={"name": "Almacén principal", "location": "Sede"},
    )
    assert response.status_code == 201
    return response.json()


def test_admin_can_manage_catalog_inventory_and_assign_materials(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    item = create_catalog_item(client, headers)
    warehouse = create_warehouse(client, headers)
    client_id = create_client(client, headers, "Cliente Inventario")
    work_order = client.post(
        "/api/v1/work-orders",
        headers=headers,
        json={"client_id": client_id, "title": "Instalación con material"},
    ).json()

    entry = client.post(
        "/api/v1/inventory/movements",
        headers=headers,
        json={
            "catalog_item_id": item["id"],
            "warehouse_id": warehouse["id"],
            "movement_type": "entry",
            "quantity": "10.000",
            "reference": "ENT-001",
        },
    )
    assert entry.status_code == 201
    assert entry.json()["quantity"] == "10.000"

    assignment = client.post(
        "/api/v1/inventory/movements",
        headers=headers,
        json={
            "catalog_item_id": item["id"],
            "warehouse_id": warehouse["id"],
            "work_order_id": work_order["id"],
            "movement_type": "assignment",
            "quantity": "3.000",
        },
    )
    assert assignment.status_code == 201
    assert assignment.json()["quantity"] == "-3.000"
    assert assignment.json()["total_cost"] == "6.00"

    inventory = client.get("/api/v1/inventory", headers=headers)
    assert inventory.status_code == 200
    assert inventory.json()[0]["stock"] == "7.000"
    assert inventory.json()[0]["available"] == "7.000"
    assert inventory.json()[0]["inventory_value"] == "14.00"

    profitability = client.get("/api/v1/profitability/summary", headers=headers)
    assert profitability.status_code == 200
    assert profitability.json()["material_costs"] == "6.00"
    assert profitability.json()["expenses_total"] == "6.00"
    assert profitability.json()["work_orders"][0]["expenses_total"] == "6.00"


def test_inventory_rejects_movements_without_stock(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    item = create_catalog_item(client, headers)
    warehouse = create_warehouse(client, headers)

    response = client.post(
        "/api/v1/inventory/movements",
        headers=headers,
        json={
            "catalog_item_id": item["id"],
            "warehouse_id": warehouse["id"],
            "movement_type": "exit",
            "quantity": "1.000",
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "No hay stock suficiente"


def test_regular_user_can_read_but_not_change_inventory(client: TestClient) -> None:
    headers = register_and_login(client)

    assert client.get("/api/v1/catalog", headers=headers).status_code == 200
    assert client.get("/api/v1/inventory", headers=headers).status_code == 200
    assert (
        client.post(
            "/api/v1/warehouses",
            headers=headers,
            json={"name": "No permitido"},
        ).status_code
        == 403
    )


def test_legacy_tariff_csv_import_is_idempotent(client: TestClient, tmp_path: Path) -> None:
    headers = create_admin_and_login(client)
    source = tmp_path / "tariff_items.csv"
    source.write_text(
        "id,code,family,description,unit,purchase_price,sale_price,labor_hours,"
        "supplier,igic_percent,active\n"
        "1,MO-ELEC,Mano de obra,Hora oficial electricista,h,0,32,1,,7,1\n"
        "2,ELE-CABLE,Electricidad,Cable manguera,m,1.15,2.25,0.03,,7,1\n",
        encoding="utf-8",
    )
    previous_path = settings.legacy_tariff_csv_path
    settings.legacy_tariff_csv_path = str(source)
    try:
        imported = client.post("/api/v1/catalog/import-legacy", headers=headers)
        assert imported.status_code == 200
        assert imported.json()["created"] == 2
        assert imported.json()["warehouse_created"] is True

        repeated = client.post("/api/v1/catalog/import-legacy", headers=headers)
        assert repeated.status_code == 200
        assert repeated.json()["created"] == 0
        assert repeated.json()["updated"] == 2

        catalog = client.get("/api/v1/catalog?limit=10", headers=headers)
        assert catalog.status_code == 200
        assert len(catalog.json()) == 2
        assert catalog.json()[0]["legacy_id"] is not None

        inventory = client.get("/api/v1/inventory", headers=headers)
        assert inventory.status_code == 200
        assert len(inventory.json()) == 2
    finally:
        settings.legacy_tariff_csv_path = previous_path
