"""Models for table creation"""

from sqlalchemy import Column, String, BIGINT, Date, Integer, Enum, ForeignKey, Boolean, Double
from sqlalchemy.sql.sqltypes import TIMESTAMP, Float, ARRAY
from sqlalchemy.sql.expression import text
from enum import Enum as PyEnum

from app.v2_0.infrastructure.database import Base


class ActivityStatus(PyEnum):
    """States the activity of a user"""
    INACTIVE = 0
    ACTIVE = 1


class RolesEnum(PyEnum):
    """Enum for roles of an employee in a company"""
    OWNER = 0
    MANAGER = 1
    ACCOUNTANT = 2
    EMPLOYEE = 3


class LeaveStatus(PyEnum):
    """States the current status of an applied leave"""
    REJECTED = 0
    PENDING = 1
    ACCEPTED = 2


class LeaveType(PyEnum):
    """States the type of leave"""
    CASUAL = 0
    MEDICAL = 1


class BranchSettings(Base):
    """Contains all the fields required in the 'BranchSettings' table"""
    __tablename__ = 'branch_settings'

    setting_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    working_days = Column(Integer, nullable=True)
    time_in = Column(String, nullable=True)
    time_out = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    default_approver = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    overtime_rate = Column(Float, nullable=True)
    overtime_rate_per = Column(String, nullable=True)
    is_hq_settings = Column(Boolean, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(Integer, nullable=False)


class Branches(Base):
    """Contains all the fields required in the 'branches' table"""
    __tablename__ = 'branches'

    branch_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=False)
    branch_name = Column(String, nullable=False)
    branch_contact = Column(BIGINT, nullable=True)
    branch_currency = Column(String, nullable=True)
    branch_address = Column(String, nullable=True)
    location = Column(String, nullable=True)
    pincode = Column(Integer, nullable=True)
    longitude = Column(Double, nullable=True)
    latitude = Column(Double, nullable=True)
    is_head_quarter = Column(Boolean, nullable=True)
    activity_status = Column(Enum(ActivityStatus), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(Integer, nullable=False)


class Companies(Base):
    """Contains all the fields required in the 'companies' table"""
    __tablename__ = "companies"
    __table_args__ = {'extend_existing': True}

    company_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    company_name = Column(String, nullable=False)
    company_domain = Column(String, nullable=True)
    company_logo = Column(String, nullable=True)
    company_email = Column(String, nullable=True)
    services = Column(String, nullable=True)
    owner = Column(Integer, ForeignKey('users_auth.user_id'), nullable=False)
    activity_status = Column(Enum(ActivityStatus), nullable=False)
    onboarding_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(Integer, nullable=False)


class UsersAuth(Base):
    """Contains all the fields required in the 'users' table"""
    __tablename__ = "users_auth"
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    password = Column(String, nullable=False)
    user_email = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    invited_by = Column(String, nullable=True)
    modified_by = Column(Integer, nullable=False)
    change_password_token = Column(String, nullable=True)


class UserCompanyBranch(Base):
    """Contains all the fields required for creating the table"""
    __tablename__ = 'user_company_branch'

    ucb_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=True)
    role = Column(Enum(RolesEnum), nullable=True)
    approvers = Column(ARRAY(Integer), nullable=False)


class Leaves(Base):
    __tablename__ = 'leaves'

    leave_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    leave_type = Column(Enum(LeaveType),nullable=False)
    leave_reason = Column(String, nullable=False)
    start_date = Column(Date,nullable=False)
    end_date = Column(Date, nullable=False)
    comment = Column(String, nullable=True)
    approvers = Column(ARRAY(Integer), nullable=False)
    leave_status = Column(Enum(LeaveStatus), nullable=True)
    is_leave_approved = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(Integer, nullable=False)


class UserDetails(Base):
    __tablename__ = 'user_details'

    details_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    user_contact = Column(BIGINT, nullable=True, unique=True)
    user_birthdate = Column(Date, nullable=True)
    medical_leaves = Column(Integer, nullable=False)
    casual_leaves = Column(Integer, nullable=False)
    user_image = Column(String, nullable=True)
    activity_status = Column(Enum(ActivityStatus), nullable=False)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
