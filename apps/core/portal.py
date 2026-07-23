from pathlib import Path


def resolve_portal_file(dist_directory: Path, request_path: str) -> Path | None:
    """Resolve a requested SPA file without allowing path traversal."""
    if not dist_directory.exists():
        return None

    base = dist_directory.resolve()
    candidate = (base / request_path).resolve()
    if candidate != base and base not in candidate.parents:
        return None
    if candidate.is_file():
        return candidate

    index = base / "index.html"
    return index if index.is_file() else None
