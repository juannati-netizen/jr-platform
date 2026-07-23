import os
from collections.abc import Generator

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["INITIAL_ADMIN_EMAIL"] = ""
os.environ["INITIAL_ADMIN_PASSWORD"] = ""
os.environ["JWT_SECRET_KEY"] = "test-secret-key-with-more-than-32-characters"

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.db.base import Base
from apps.db.session import engine
from apps.models import (
    AiConfiguration,
    CatalogItem,
    Client,
    CompanyProfile,
    ConfigurationEvent,
    CrmActivity,
    Expense,
    FiscalYear,
    InventoryLevel,
    Invoice,
    InvoiceItem,
    Lead,
    Opportunity,
    OpportunityStageHistory,
    Payment,
    Project,
    ProjectDocument,
    Quote,
    QuoteItem,
    StockMovement,
    Supplier,
    User,
    VerifactuConfiguration,
    Warehouse,
    WorkOrder,
    WorkOrderNote,
)

_ = (
    AiConfiguration,
    CatalogItem,
    Client,
    CompanyProfile,
    ConfigurationEvent,
    CrmActivity,
    Expense,
    FiscalYear,
    InventoryLevel,
    Invoice,
    InvoiceItem,
    Lead,
    Opportunity,
    OpportunityStageHistory,
    Payment,
    Project,
    ProjectDocument,
    Quote,
    QuoteItem,
    StockMovement,
    Supplier,
    User,
    VerifactuConfiguration,
    Warehouse,
    WorkOrder,
    WorkOrderNote,
)


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
