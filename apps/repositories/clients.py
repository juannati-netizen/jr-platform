from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.models.client import Client
from apps.schemas.client import ClientCreate, ClientUpdate


class DuplicateTaxIdError(Exception):
    pass


def get_client(db: Session, client_id: str) -> Client | None:
    return db.get(Client, client_id)


def list_clients(
    db: Session,
    *,
    search: str | None = None,
    active_only: bool = False,
) -> list[Client]:
    statement = select(Client)
    if active_only:
        statement = statement.where(Client.is_active.is_(True))
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Client.name.ilike(pattern),
                Client.tax_id.ilike(pattern),
                Client.email.ilike(pattern),
            )
        )
    statement = statement.order_by(Client.name)
    return list(db.scalars(statement).all())


def create_client(db: Session, payload: ClientCreate) -> Client:
    client = Client(
        name=payload.name,
        tax_id=payload.tax_id.strip().upper() if payload.tax_id else None,
        email=str(payload.email).lower() if payload.email else None,
        phone=payload.phone.strip() if payload.phone else None,
        address=payload.address.strip() if payload.address else None,
        notes=payload.notes.strip() if payload.notes else None,
    )
    db.add(client)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateTaxIdError from exc
    db.refresh(client)
    return client


def update_client(db: Session, client: Client, payload: ClientUpdate) -> Client:
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes and payload.name is not None:
        client.name = payload.name
    if "tax_id" in changes:
        client.tax_id = payload.tax_id.strip().upper() if payload.tax_id else None
    if "email" in changes:
        client.email = str(payload.email).lower() if payload.email else None
    if "phone" in changes:
        client.phone = payload.phone.strip() if payload.phone else None
    if "address" in changes:
        client.address = payload.address.strip() if payload.address else None
    if "notes" in changes:
        client.notes = payload.notes.strip() if payload.notes else None
    if "is_active" in changes and payload.is_active is not None:
        client.is_active = payload.is_active

    db.add(client)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateTaxIdError from exc
    db.refresh(client)
    return client
