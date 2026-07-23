from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from apps.api import main as api_main


def test_root_returns_api_metadata_without_built_portal(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(api_main, "PORTAL_DIST", tmp_path / "missing-portal")

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "JR Platform API"
    assert response.json()["version"] == "0.13.0"
