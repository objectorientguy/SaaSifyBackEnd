"""Schemas for Company"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.v2_0.domain.models.enums import ActivityStatus
from app.v2_0.domain.schemas.modifier_schemas import Modifier
from app.v2_0.domain.schemas.branch_schemas import AddBranch


class UpdateCompany(Modifier):
    company_name: str
    company_domain: str = None
    company_logo: str = None
    company_email: str = None
    services: str = None
    owner: int = None
    activity_status: ActivityStatus = "ACTIVE"


class AddCompany(AddBranch, UpdateCompany):
    """Contains all the fields that will be accessible to all objects of type - 'Company' """
    onboarding_date: date = datetime.now()


class GetCompany(BaseModel):
    company_id: int
    company_name: Optional[str]
    owner: Optional[int]
    activity_status: Optional[ActivityStatus]