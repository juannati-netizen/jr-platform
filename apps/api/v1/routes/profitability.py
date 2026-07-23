from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import require_roles
from apps.db.session import get_db
from apps.models.user import User, UserRole
from apps.repositories.procurement import get_profitability_summary
from apps.schemas.procurement import ProfitabilitySummary

router = APIRouter()


@router.get("/summary", response_model=ProfitabilitySummary)
def read_profitability_summary(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> ProfitabilitySummary:
    return get_profitability_summary(db)
