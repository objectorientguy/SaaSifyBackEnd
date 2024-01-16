from sqlalchemy import Column, String, Integer, BIGINT, ForeignKey, Date, Enum
from sqlalchemy.orm import validates, relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP, Boolean, Float, JSON, Double, DateTime
from enum import Enum as PyEnum

from app.infrastructure.database import Base


class ActivityStatus(PyEnum):
    ACTIVE = 1
    INACTIVE = 0


class HalfDayStatus(PyEnum):
    NO_HALF_DAY = 0
    FIRST_HALF = 1
    SECOND_HALF = 2


class RolesEnum(PyEnum):
    OWNER = 1
    EMPLOYEE = 2
    MANAGER = 3
    ACCOUNTANT = 4


class CompaniesV(Base):
    __tablename__ = "companies1"
    __table_args__ = {'extend_existing': True}

    company_id = Column(String, nullable=False, primary_key=True, unique=True,
                        server_default=text("EXTRACT(EPOCH FROM NOW())::BIGINT"))
    company_name = Column(String, nullable=False)
    company_domain = Column(String, nullable=True)
    company_logo = Column(String, nullable=True)
    company_email = Column(String, nullable=True)
    services = Column(String, nullable=True)
    owner = Column(String, ForeignKey('users1.user_id'), nullable=False)
    onboarding_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(String, ForeignKey("users1.user_id"), nullable=False)

    @validates('company_name', 'company_email', 'company_contact')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class Modules(Base):
    __tablename__ = "modules"

    module_id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
    module_name = Column(String, nullable=False)
    base_cost = Column(Float, nullable=False)


class Roles(Base):
    __tablename__ = "roles"

    role_id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
    role_name = Column(Enum(RolesEnum), nullable=False)


class UsersV(Base):
    __tablename__ = "users1"
    __table_args__ = {'extend_existing': True}

    user_id = Column(String, primary_key=True, nullable=False, unique=True)
    user_name = Column(String, nullable=False)
    user_contact = Column(BIGINT, nullable=True, unique=True)
    user_email = Column(String, nullable=True, unique=True)
    user_birthdate = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    user_image = Column(String, nullable=True)

    @validates('user_contact', 'user_id', 'user_name', 'user_email')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class Branches(Base):
    __tablename__ = 'branches'

    branch_id = Column(BIGINT, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey('companies1.company_id'), nullable=False)
    branch_name = Column(String, nullable=False)
    branch_address = Column(String, nullable=False)
    branch_currency = Column(String, nullable=False)
    branch_active = Column(Boolean, nullable=False, server_default='TRUE')
    branch_contact = Column(BIGINT, nullable=True)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(String, ForeignKey("users1.user_id"), nullable=False)
    location = Column(String, nullable=False)

    company = relationship("Companies")

    @validates('company_id', 'branch_name', 'branch_currency', 'branch_contact')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class UserAuthentication(Base):
    __tablename__ = 'user_auth'
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(String, ForeignKey('users1.user_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies1.company_id'), nullable=False)
    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'), nullable=True)
    module_id = Column(BIGINT, ForeignKey('modules.module_id'), nullable=True)
    role_id = Column(BIGINT, ForeignKey('roles.role_id'), nullable=True)

    company = relationship("Companies")
    user = relationship("UsersV")


# class UserCompany(Base):
#     __tablename__ = 'user_company'
#
#     id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
#     user_id = Column(String, ForeignKey('users1.user_id'), nullable=False)
#     company_id = Column(String, ForeignKey('companies1.company_id'), nullable=False)
#
#     company = relationship("Companies")
#     user = relationship("UsersV")


class Brand(Base):
    __tablename__ = 'brand'

    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'))
    company_id = Column(String, ForeignKey('companies1.company_id'), nullable=False)
    brand_id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
    brand_name = Column(String, nullable=False)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(String, ForeignKey("users1.user_id"), nullable=False)

    company = relationship("Companies")
    branch = relationship("Branches")

    @validates('company_id', 'branch_id', 'brand_name')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class Category(Base):
    __tablename__ = 'category'

    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'))
    company_id = Column(String, ForeignKey('companies1.company_id'), nullable=False)
    category_id = Column(BIGINT, primary_key=True, autoincrement=True)
    category_name = Column(String, nullable=False)
    is_active = Column(Boolean, server_default='TRUE', nullable=False)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(String, ForeignKey("users1.user_id"), nullable=False)

    company = relationship("Companies")
    branch = relationship("Branches")

    @validates('company_id', 'branch_id', 'category_name', 'is_active')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class PaymentMethod(Base):
    __tablename__ = 'payment_method'

    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies1.company_id'), nullable=False)
    payment_id = Column(BIGINT, primary_key=True, autoincrement=True)
    payment_name = Column(String, nullable=False)
    is_active = Column(Boolean, server_default='TRUE', nullable=False)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(String, ForeignKey("users1.user_id"), nullable=False)

    company = relationship("Companies")
    branch = relationship("Branches")

    @validates('company_id', 'branch_id', 'payment_name', 'is_active')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class Products(Base):
    __tablename__ = 'products'

    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies1.company_id'), nullable=False)
    brand_id = Column(BIGINT, ForeignKey('brand.brand_id'), nullable=True)
    category_id = Column(BIGINT, ForeignKey('category.category_id'), nullable=False)
    product_id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
    product_name = Column(String, nullable=False)
    product_description = Column(String, nullable=True)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(String, ForeignKey("users1.user_id"), nullable=False)

    company = relationship("Companies")
    branch = relationship("Branches")
    brand = relationship("Brand")
    category = relationship("Category")
    variants = relationship('Variants', back_populates='product')

    @validates('company_id', 'branch_id', 'product_name', )
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class Variants(Base):
    __tablename__ = 'variants'

    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies1.company_id'), nullable=False)
    product_id = Column(BIGINT, ForeignKey('products.product_id', ondelete="CASCADE"), nullable=False)
    variant_id = Column(BIGINT, primary_key=True, autoincrement=True)
    cost = Column(Double, nullable=True)
    stock_id = Column(BIGINT, ForeignKey("inventory.stock_id", ondelete="CASCADE"), nullable=True)
    quantity = Column(BIGINT, nullable=True)
    unit = Column(String, nullable=True)
    discount_cost = Column(Double, nullable=True)
    discount_percent = Column(Double, nullable=True)
    images = Column(JSON, nullable=True)
    draft = Column(Boolean, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default='TRUE')
    barcode = Column(BIGINT, nullable=True)
    restock_reminder = Column(BIGINT, nullable=True)
    SGST = Column(Float, nullable=True)
    CGST = Column(Float, nullable=True)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(String, ForeignKey("users1.user_id"), nullable=False)

    company = relationship("Companies", foreign_keys=[company_id])
    branch = relationship("Branches", foreign_keys=[branch_id])
    product = relationship("Products", foreign_keys=[product_id])
    stock = relationship("Inventory", foreign_keys=[stock_id])

    @validates('company_id', 'branch_id', 'product_name', 'barcode')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class Inventory(Base):
    __tablename__ = 'inventory'

    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies1.company_id'), nullable=False)
    variant_id = Column(BIGINT, ForeignKey("variants.variant_id", ondelete="CASCADE"), nullable=True)
    stock_id = Column(BIGINT, primary_key=True, autoincrement=True)
    stock = Column(BIGINT, nullable=True)

    company = relationship("Companies", foreign_keys=[company_id])
    branch = relationship("Branches", foreign_keys=[branch_id])
    variants = relationship("Variants", foreign_keys=[variant_id])
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(String, ForeignKey("users1.user_id"), nullable=False)


class Orders(Base):
    __tablename__ = 'orders'

    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies1.company_id'), nullable=False)
    order_id = Column(BIGINT, primary_key=True, autoincrement=True)
    order_no = Column(String, nullable=False, primary_key=True, unique=True,
                      server_default=text("EXTRACT(EPOCH FROM NOW())::BIGINT"))
    order_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    items_ordered = Column(JSON, nullable=False)
    discount_total = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    payment_status = Column(String, nullable=False)
    payment_type = Column(String, nullable=False)
    customer_contact = Column(BIGINT, nullable=False)
    customer_name = Column(String, nullable=True)
    gst = Column(String, nullable=True)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(String, ForeignKey("users1.user_id"), nullable=False)

    company = relationship("Companies")
    branch = relationship("Branches")


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {'extend_existing': True}

    customer_id = Column(BIGINT, primary_key=True, nullable=False, unique=True, autoincrement=True)
    company_id = Column(String, ForeignKey("companies1.company_id"), nullable=False)
    customer_name = Column(String, nullable=False)
    customer_number = Column(String, nullable=False, unique=True)
    customer_address = Column(String, nullable=True)
    customer_birthdate = Column(Date, nullable=True)
    onboarding_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    customer_points = Column(Integer, nullable=True)
    customer_status = Column(Enum(ActivityStatus), nullable=False)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(String, ForeignKey("users1.user_id"), nullable=False)


class Employee(Base):
    __tablename__ = 'employee'

    company_id = Column(String, ForeignKey('companies1.company_id'), nullable=False)
    employee_id = Column(String, ForeignKey('users1.user_id'), primary_key=True)
    employee_email = Column(String, ForeignKey('users1.user_email'), nullable=False)
    employee_name = Column(String, nullable=True)
    employee_contact = Column(BIGINT, nullable=False)
    employee_gender = Column(String, nullable=True)
    DOJ = Column(Date, nullable=False)
    DOB = Column(Date, nullable=False)
    employee_address = Column(String, nullable=False)
    aadhar_no = Column(BIGINT, nullable=False)
    pan_no = Column(BIGINT, nullable=False)
    employee_image = Column(String, nullable=False)
    employee_ifsc_code = Column(String, nullable=False)
    employee_acc_no = Column(BIGINT, nullable=False)
    employee_bank_name = Column(String, nullable=False)
    employee_upi_code = Column(String, nullable=False)
    employee_salary = Column(Float, nullable=False)
    active_status = Column(Enum(ActivityStatus), nullable=False)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(String, ForeignKey("users1.user_id"), nullable=False)

    company = relationship("Companies")


class EmployeeLeaves(Base):
    __tablename__ = 'employee_leaves'

    leave_id = Column(BIGINT, primary_key=True, index=True)
    employee_id = Column(String, ForeignKey('employee.employee_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies1.company_id'), nullable=False)
    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'), nullable=False)
    leave_from = Column(Date, nullable=False)
    leave_till = Column(Date, nullable=False)
    reason = Column(String, nullable=False)
    half_day_status = Column(Enum(HalfDayStatus), nullable=False)
    leave_approved = Column(Boolean, nullable=True)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(String, ForeignKey("users1.user_id"), nullable=False)

    employee = relationship("Employee")


class EmployeeTimeRecord(Base):
    __tablename__ = "employee_time_records"

    time_record_id = Column(BIGINT, primary_key=True, index=True)
    company_id = Column(String, ForeignKey('companies1.company_id'), nullable=False)
    employee_id = Column(String, ForeignKey("employee.employee_id"), nullable=False)
    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'), nullable=False)
    time_in = Column(DateTime(timezone=True), server_default=text('now()'))
    time_out = Column(DateTime(timezone=True), nullable=True)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_by = Column(String, ForeignKey("users1.user_id"), nullable=False)

    employee = relationship("Employee")

    @property
    def time_difference(self):
        if self.time_out and self.time_in:
            return self.time_out - self.time_in
        else:
            return None
