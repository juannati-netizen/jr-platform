from pathlib import Path

from fastapi.testclient import TestClient

from apps.core.config import normalize_database_url
from apps.core.portal import resolve_portal_file


def test_render_database_url_uses_psycopg_driver() -> None:
    value = "postgresql://user:password@host:5432/database"
    assert normalize_database_url(value) == (
        "postgresql+psycopg://user:password@host:5432/database"
    )


def test_legacy_postgres_url_uses_psycopg_driver() -> None:
    value = "postgres://user:password@host:5432/database"
    assert normalize_database_url(value) == (
        "postgresql+psycopg://user:password@host:5432/database"
    )


def test_supabase_session_pooler_url_uses_psycopg_driver() -> None:
    value = (
        "postgresql://postgres.project:password@aws-0-eu-central-1.pooler.supabase.com:"
        "5432/postgres?sslmode=require"
    )
    assert normalize_database_url(value) == (
        "postgresql+psycopg://postgres.project:password@"
        "aws-0-eu-central-1.pooler.supabase.com:5432/postgres?sslmode=require"
    )


def test_free_render_blueprint_uses_external_database() -> None:
    blueprint = (Path(__file__).resolve().parents[1] / "render.yaml").read_text(encoding="utf-8")

    assert "plan: free" in blueprint
    assert "- key: DATABASE_URL\n        sync: false" in blueprint
    assert "databases:" not in blueprint
    assert "basic-256mb" not in blueprint
    assert "plan: starter" not in blueprint


def test_portal_fallback_resolves_index(tmp_path: Path) -> None:
    index = tmp_path / "index.html"
    index.write_text("<html>JR Platform</html>", encoding="utf-8")

    assert resolve_portal_file(tmp_path, "dashboard") == index.resolve()


def test_portal_file_resolver_blocks_path_traversal(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("portal", encoding="utf-8")
    outside = tmp_path.parent / "secret.txt"
    outside.write_text("secret", encoding="utf-8")

    assert resolve_portal_file(tmp_path, "../secret.txt") is None


def test_security_headers_are_enabled(client: TestClient) -> None:
    response = client.get("/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
