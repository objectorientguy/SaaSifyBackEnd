"""Apis are intercepted in this file"""
from typing import List

from fastapi import APIRouter
from fastapi import Depends

from app.infrastructure.database import engine, get_db
from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.password_handler.pwd_encrypter_decrypter import verify
from app.v2_0.application.password_handler.reset_password import initiate_pwd_reset, check_token, change_password
from app.v2_0.application.service.company_service import add_company, add_branch, fetch_company, modify_company, \
    modify_branch, fetch_branches, get_all_user_data
from app.v2_0.application.service.employee_service import add_employee, new_emp_in_company
from app.v2_0.domain import models_2

from app.v2_0.domain.schema_2 import AddUser, PwdResetToken, JSONObject, Credentials, AddCompany, AddBranch, \
    UpdateUser, UpdateCompany, UpdateBranch, GetCompany, GetBranch, NewEmployee
from app.v2_0.application.service.user_service import add_user, modify_user

router = APIRouter()
models_2.Base_2.metadata.create_all(bind=engine)


@router.post("/v2.0/newUser")
def register_user(user: AddUser, db=Depends(get_db)):
    """Calls service layer to create a new user"""
    return add_user(user, db)


@router.put("/v2.0/updateUser/{user_id}")
def update_user(user: UpdateUser, user_id: int, db=Depends(get_db)):
    """Calls service layer to update user"""
    return modify_user(user, user_id, db)


@router.post("/v2.0/login")
def login(credentials: Credentials, db=Depends(get_db)):
    """Individual Login"""
    email = credentials.model_dump()["email"]
    pwd = credentials.model_dump()["password"]
    is_user_present = db.query(models_2.Users).filter(models_2.Users.user_email == email).first()

    if not is_user_present:
        return ResponseDTO("404", "User is not registered, please register.", {})

    if not verify(pwd, is_user_present.password):
        return ResponseDTO("401", "Password Incorrect!", {})

    # Get all user data
    ucb = db.query(models_2.UserCompanyBranch).filter(
        models_2.UserCompanyBranch.user_id == is_user_present.user_id).first()
    if ucb.company_id is None:
        data = []
    else:

        complete_data = get_all_user_data(is_user_present,ucb, db)
        data = [complete_data]

    return ResponseDTO("200", "Login successful",
                       {"user_id": is_user_present.user_id, "company": data})


@router.post("/v2.0/forgotPassword")
def forgot_password(user_email: JSONObject, db=Depends(get_db)):
    """Calls the service layer to send an email for password reset"""
    return initiate_pwd_reset(user_email.model_dump()["email"], db)


@router.post("/v2.0/sendVerificationLink")
def verify_token(token: PwdResetToken, db=Depends(get_db)):
    """Calls the service layer to verify the token received by an individual"""
    return check_token(token.model_dump()["token"], db)


@router.put("/v2.0/updatePassword")
def update_password(obj: Credentials, db=Depends(get_db)):
    """Calls the service layer to update the password of an individual"""
    return change_password(obj, db)


@router.post("/v2.0/{user_id}/createCompany")
def create_company(company: AddCompany, user_id: int, db=Depends(get_db)):
    return add_company(company, user_id, db)


@router.get("/v2.0/{user_id}/getCompany", response_model=GetCompany)
def get_company(user_id: int, db=Depends(get_db)):
    return fetch_company(user_id, db)


@router.put("/v2.0/{user_id}/updateCompany")
def update_company(company: UpdateCompany, user_id: int, db=Depends(get_db)):
    return modify_company(company, user_id, db)


@router.post("/v2.0/{user_id}/{company_id}/createBranch")
def create_branch(branch: AddBranch, user_id: int, company_id: int, db=Depends(get_db)):
    return add_branch(branch, user_id, company_id, db)


@router.put("/v2.0/{user_id}/{company_id}/updateBranch/{branch_id}")
def update_branch(branch: UpdateBranch, user_id: int, branch_id: int, company_id: int, db=Depends(get_db)):
    return modify_branch(branch, user_id, branch_id, company_id, db)


@router.get("/v2.0/{company_id}/getBranches", response_model=List[GetBranch])
def get_branches(company_id: int, db=Depends(get_db)):
    return fetch_branches(company_id, db)


@router.post("/v2.0/sendInvite")
def send_employee_invite(user: AddUser, db=Depends(get_db)):
    return add_employee(user, db)


@router.post("/v2.0/addEmployeeInCompany")
def add_employee_in_company(employee: NewEmployee, db=Depends(get_db)):
    return new_emp_in_company(employee, db)
