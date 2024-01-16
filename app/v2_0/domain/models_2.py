"""Models for table creation"""

from sqlalchemy import Column, String, BIGINT, Date, Integer, Enum, ForeignKey, Boolean
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from enum import Enum as PyEnum

from app.infrastructure.database import Base_2


class ActivityStatus(PyEnum):
    INACTIVE = 0
    ACTIVE = 1


class RolesEnum(PyEnum):
    """Enum for roles of an employee in a company"""
    OWNER = 0
    MANAGER = 1
    ACCOUNTANT = 2
    EMPLOYEE = 3


class Branches(Base_2):
    """Contains all the fields required in the 'branches' table"""
    __tablename__ = 'branches'

    branch_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=False)
    branch_name = Column(String, nullable=False)
    branch_contact = Column(BIGINT, nullable=True)
    branch_currency = Column(String, nullable=True)
    branch_address = Column(String, nullable=True)
    location = Column(String, nullable=True)
    is_head_quarter = Column(Boolean, nullable=True)
    activity_status = Column(Enum(ActivityStatus), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(Integer, nullable=False)


class Companies(Base_2):
    """Contains all the fields required in the 'companies' table"""
    __tablename__ = "companies"
    __table_args__ = {'extend_existing': True}

    company_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    company_name = Column(String, nullable=False)
    company_domain = Column(String, nullable=True)
    company_logo = Column(String, nullable=True)
    company_email = Column(String, nullable=True)
    services = Column(String, nullable=True)
    owner = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    activity_status = Column(Enum(ActivityStatus), nullable=False)
    onboarding_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(Integer, nullable=False)


class Users(Base_2):
    """Contains all the fields required in the 'users' table"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    user_contact = Column(BIGINT, nullable=True, unique=True)
    user_email = Column(String, nullable=True, unique=True)
    user_birthdate = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(Integer, nullable=False)
    user_image = Column(String, nullable=True)
    activity_status = Column(Enum(ActivityStatus), nullable=False)
    change_password_token = Column(String, nullable=True)


class UserCompanyBranch(Base_2):
    """Contains all the fields required for creating the table"""
    __tablename__ = 'user_company_branch'

    ucb_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=True)
    role = Column(Enum(RolesEnum), nullable=True)
