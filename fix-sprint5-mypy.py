from pathlib import Path


def fix_finance_schema() -> None:
    path = Path("apps/schemas/finance.py")
    text = path.read_text(encoding="utf-8")

    old = "from apps.schemas.work_order import ClientReference, UserReference"
    new = (
        "from apps.schemas.client import ClientReference\n"
        "from apps.schemas.work_order import UserReference"
    )

    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise RuntimeError("No se encontró el import esperado en apps/schemas/finance.py")

    path.write_text(text, encoding="utf-8")


def fix_profitability_loops() -> None:
    path = Path("apps/repositories/procurement.py")
    lines = path.read_text(encoding="utf-8").splitlines()
    output: list[str] = []
    mode: str | None = None
    found_work_orders = False
    found_clients = False

    for line in lines:
        stripped = line.strip()

        if stripped == "for item in work_orders:":
            indent = line[: len(line) - len(line.lstrip())]
            line = f"{indent}for work_order in work_orders:"
            mode = "work_order"
            found_work_orders = True
        elif stripped.startswith("work_order_report.sort("):
            mode = None
        elif stripped == "for item in clients:":
            indent = line[: len(line) - len(line.lstrip())]
            line = f"{indent}for client in clients:"
            mode = "client"
            found_clients = True
        elif stripped.startswith("client_report.sort("):
            mode = None

        if mode == "work_order":
            line = line.replace("item.", "work_order.")
        elif mode == "client":
            line = line.replace("item.", "client.")

        output.append(line)

    if not found_work_orders and "for work_order in work_orders:" not in "\n".join(output):
        raise RuntimeError("No se encontró el bucle de trabajos esperado en procurement.py")
    if not found_clients and "for client in clients:" not in "\n".join(output):
        raise RuntimeError("No se encontró el bucle de clientes esperado en procurement.py")

    path.write_text("\n".join(output) + "\n", encoding="utf-8")


if __name__ == "__main__":
    fix_finance_schema()
    fix_profitability_loops()
    print("Corrección Sprint 5 aplicada correctamente.")
