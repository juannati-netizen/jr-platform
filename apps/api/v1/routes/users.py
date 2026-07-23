from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import get_current_user, require_roles
from apps.db.session import get_db
from apps.models.user import User, UserRole
from apps.repositories.users import get_user_by_id, list_users, update_user_role
from apps.schemas.user import UserRead, UserRoleUpdate

router = APIRouter()


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    return UserRead.model_validate(current_user)


@router.get("", response_model=list[UserRead])
def read_users(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> list[UserRead]:
    return [UserRead.model_validate(user) for user in list_users(db)]


@router.patch("/{user_id}/role", response_model=UserRead)
def change_user_role(
    user_id: str,
    payload: UserRoleUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> UserRead:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    updated_user = update_user_role(db, user, payload.role)
    return UserRead.model_validate(updated_user)
