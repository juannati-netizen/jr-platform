from apps.core.config import settings
from apps.db.session import SessionLocal
from apps.models.user import UserRole
from apps.repositories.users import create_user, get_user_by_email
from apps.schemas.user import UserCreate


def create_initial_admin() -> None:
    if not settings.initial_admin_email or not settings.initial_admin_password:
        return

    email = settings.initial_admin_email.lower()
    with SessionLocal() as db:
        if get_user_by_email(db, email) is not None:
            return

        create_user(
            db,
            UserCreate(
                email=email,
                full_name=settings.initial_admin_full_name,
                password=settings.initial_admin_password,
            ),
            role=UserRole.ADMIN,
        )
