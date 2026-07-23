from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import get_current_user
from apps.db.session import get_db
from apps.models.user import User
from apps.repositories.dashboard import get_dashboard_summary
from apps.schemas.dashboard import DashboardSummary

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def read_dashboard_summary(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> DashboardSummary:
    return get_dashboard_summary(db)
