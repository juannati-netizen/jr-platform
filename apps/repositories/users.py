from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.core.security import hash_password
from apps.models.user import User, UserRole
from apps.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.get(User, user_id)


def list_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at)).all())


def create_user(
    db: Session,
    payload: UserCreate,
    *,
    role: UserRole = UserRole.USER,
) -> User:
    user = User(
        email=str(payload.email).lower(),
        full_name=payload.full_name.strip(),
        hashed_password=hash_password(payload.password),
        role=role.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_role(db: Session, user: User, role: UserRole) -> User:
    user.role = role.value
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
