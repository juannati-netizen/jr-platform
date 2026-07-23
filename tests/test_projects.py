from fastapi.testclient import TestClient

from tests.helpers import create_admin_and_login, create_client


def create_work_order(
    client: TestClient,
    headers: dict[str, str],
    client_id: str,
) -> str:
    response = client.post(
        "/api/v1/work-orders",
        headers=headers,
        json={
            "client_id": client_id,
            "title": "Reforma eléctrica",
            "status": "planned",
            "priority": "normal",
        },
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def create_project(
    client: TestClient,
    headers: dict[str, str],
    client_id: str,
    work_order_id: str,
) -> str:
    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "name": "Obra nave industrial",
            "client_id": client_id,
            "work_order_id": work_order_id,
            "status": "active",
            "budget": "12000.00",
        },
    )
    assert response.status_code == 201
    assert response.json()["code"].startswith("OBR-")
    return str(response.json()["id"])


def test_project_file_aggregates_work_order(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    client_id = create_client(client, headers)
    work_order_id = create_work_order(client, headers, client_id)
    project_id = create_project(client, headers, client_id, work_order_id)

    response = client.get(f"/api/v1/projects/{project_id}/file", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["project"]["name"] == "Obra nave industrial"
    assert payload["work_order"]["id"] == work_order_id
    assert payload["financial"]["gross_margin"] == "0.00"


def test_project_document_upload_download_and_delete(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    client_id = create_client(client, headers)
    work_order_id = create_work_order(client, headers, client_id)
    project_id = create_project(client, headers, client_id, work_order_id)

    upload = client.post(
        f"/api/v1/projects/{project_id}/documents",
        headers=headers,
        data={"category": "Contrato", "notes": "Firmado"},
        files={"file": ("contrato.txt", b"contenido de prueba", "text/plain")},
    )
    assert upload.status_code == 201
    document_id = upload.json()["id"]
    assert upload.json()["size_bytes"] == 19

    download = client.get(
        f"/api/v1/projects/documents/{document_id}/download",
        headers=headers,
    )
    assert download.status_code == 200
    assert download.content == b"contenido de prueba"

    deletion = client.delete(
        f"/api/v1/projects/documents/{document_id}",
        headers=headers,
    )
    assert deletion.status_code == 204


def test_work_order_can_only_belong_to_one_project(client: TestClient) -> None:
    headers = create_admin_and_login(client)
    client_id = create_client(client, headers)
    work_order_id = create_work_order(client, headers, client_id)
    create_project(client, headers, client_id, work_order_id)

    duplicate = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "name": "Obra duplicada",
            "client_id": client_id,
            "work_order_id": work_order_id,
        },
    )
    assert duplicate.status_code == 409
