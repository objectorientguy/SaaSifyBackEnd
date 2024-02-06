"""Service layer for Companies"""
from datetime import datetime, time

from sqlalchemy import select

from app.v2_0.application.dto.dto_classes import ResponseDTO
from app.v2_0.application.utility.app_utility import check_if_company_and_branch_exist, add_company_to_ucb, \
    add_branch_to_ucb
from app.v2_0.domain.models.branch_settings import BranchSettings
from app.v2_0.domain.models.branches import Branches
from app.v2_0.domain.models.companies import Companies
from app.v2_0.domain.models.enums import ActivityStatus
from app.v2_0.domain.models.user_auth import UsersAuth
from app.v2_0.domain.models.user_company_branch import UserCompanyBranch
from app.v2_0.domain.models.user_details import UserDetails
from app.v2_0.domain.schemas.branch_schemas import AddBranch, CreateBranchResponse
from app.v2_0.domain.schemas.branch_settings_schemas import GetBranchSettings, BranchSettingsSchema
from app.v2_0.domain.schemas.company_schemas import GetCompany, AddCompanyResponse
from app.v2_0.domain.schemas.utility_schemas import UserDataResponse, GetUserDataResponse


def set_employee_leaves(settings, company_id, db):
    users = db.query(UserCompanyBranch).filter(UserCompanyBranch.company_id == company_id).all()
    user_id_array = []
    for user in users:
        user_id_array.append(user.user_id)
    for ID in user_id_array:
        query = db.query(UserDetails).filter(UserDetails.user_id == ID)
        u = query.first()
        if u is None:
            return ResponseDTO(404, "User not found!", {})
        if u.medical_leaves is None and u.casual_leaves is None:
            query.update(
                {"medical_leaves": settings.total_medical_leaves, "casual_leaves": settings.total_casual_leaves})
            db.commit()


def modify_branch_settings(settings, user_id, company_id, branch_id, db):
    """Updates the branch settings"""

    check = check_if_company_and_branch_exist(company_id, branch_id, db)

    if check is None:
        existing_settings_query = db.query(BranchSettings).filter(
            BranchSettings.branch_id == branch_id)
        settings.modified_on = datetime.now()
        settings.modified_by = user_id
        company = db.query(Companies).filter(Companies.company_id == existing_settings_query.first().company_id).first()

        if settings.default_approver != company.owner:
            return ResponseDTO(400, "Default approver should be the company owner!", {})

        existing_settings_query.update(settings.__dict__)
        db.commit()
        set_employee_leaves(settings, company_id, db)

        return ResponseDTO(200, "Settings updated", {})
    else:
        return check


def fetch_branch_settings(user_id, company_id, branch_id, db):
    """Fetches the branch settings"""
    try:

        user_exists = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
        if user_exists is None:
            return ResponseDTO(404, "User does not exist!", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            settings = db.query(BranchSettings).filter(BranchSettings.branch_id == branch_id).first()

            if settings is None:
                return ResponseDTO(404, "Settings do not exist!", {})

            result = GetBranchSettings(**settings.__dict__)

            return ResponseDTO(200, "Settings fetched!", result)
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def import_hq_settings(branch_id, company_id, user_id, db):
    """It copies the settings of headquarters branch to other branches"""
    try:
        hq_settings = db.query(BranchSettings).filter(
            BranchSettings.company_id == company_id).filter(
            BranchSettings.is_hq_settings == "true").first()
        imported_settings = BranchSettings(branch_id=branch_id, company_id=company_id,
                                           is_hq_settings=False,
                                           default_approver=hq_settings.default_approver,
                                           working_days=hq_settings.working_days, total_casual_leaves=3,
                                           total_medical_leaves=12,
                                           time_in=hq_settings.time_in, time_out=hq_settings.time_out,
                                           timezone=hq_settings.timezone, currency=hq_settings.currency,
                                           overtime_rate=hq_settings.overtime_rate,
                                           overtime_rate_per=hq_settings.overtime_rate_per)
        db.add(imported_settings)
        db.flush()

        return ResponseDTO(200, "Settings Imported successfully", {})
    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})


def add_branch_settings(company_settings, user_id, db):
    """Adds settings to a branch"""
    try:
        get_branch = db.query(Branches).filter(Branches.branch_id == company_settings.branch_id).first()

        if get_branch.is_head_quarter is True:
            new_settings = BranchSettings(branch_id=company_settings.branch_id,
                                          time_in=datetime.combine(datetime.now().date(), time(9, 30)),
                                          time_out=datetime.combine(datetime.now().date(), time(18, 30)),
                                          company_id=company_settings.company_id,
                                          is_hq_settings=True, total_casual_leaves=3,
                                          total_medical_leaves=12,overtime_rate_per="HOUR",
                                          default_approver=company_settings.default_approver)
            db.add(new_settings)
            db.flush()

        else:
            import_hq_settings(company_settings.branch_id, company_settings.company_id, user_id, db)

        return ResponseDTO(200, "Settings added!", {})
    except Exception as exc:
        db.rollback()
        return ResponseDTO(204, str(exc), {})


def set_branch_settings(new_branch, user_id, company_id, db):
    """Sets the branch settings"""
    company_settings = BranchSettingsSchema
    company_settings.branch_id = new_branch.branch_id
    company_settings.default_approver = user_id
    company_settings.company_id = company_id

    add_branch_settings(company_settings, user_id, db)


def add_branch(branch, user_id, company_id, db, is_init: bool):
    """Creates a branch for a company"""
    try:
        company_exists = db.query(Companies).filter(Companies.company_id == company_id).first()
        if company_exists is None:
            return ResponseDTO(404, "Company not found!", {})

        new_branch = Branches(branch_name=branch.branch_name, company_id=company_id,
                              activity_status=ActivityStatus.ACTIVE,
                              is_head_quarter=branch.is_head_quarter)
        db.add(new_branch)
        db.flush()

        # Adds the branch in Users_Company_Branches table
        add_branch_to_ucb(new_branch, user_id, company_id, db)
        set_branch_settings(new_branch, user_id, company_id, db)
        db.commit()

        if is_init:
            return CreateBranchResponse(branch_name=new_branch.branch_name, branch_id=new_branch.branch_id, modules=[])
        else:
            return ResponseDTO(200, "Branch created successfully!",
                               CreateBranchResponse(branch_name=new_branch.branch_name, branch_id=new_branch.branch_id,
                                                    modules=[]))
    except Exception as exc:
        db.rollback()
        # if db.in_transaction:
        #     return ResponseDTO(200, "The session was rolled back", {})
        return ResponseDTO(204, str(exc), {})


def fetch_branches(user_id, company_id, branch_id, db):
    """Fetches the branches of given company"""
    try:
        user = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
        if user is None:
            ResponseDTO(404, "User not found!", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            branches = db.query(Branches).filter(Branches.company_id == company_id).all()
            return ResponseDTO(200, "Branches fetched!", branches)
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def modify_branch(branch, user_id, company_id, branch_id, bran_id, db):
    """Updates a branch"""
    try:
        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            branch_query = db.query(Branches).filter(Branches.branch_id == bran_id)

            if branch_query.first() is None:
                return ResponseDTO(404, "Branch to be updated does not exist!", {})

            branch.modified_by = user_id
            branch.modified_on = datetime.now()
            branch.company_id = company_id
            branch_query.update(branch.__dict__)
            db.commit()

            return ResponseDTO(200, "Branch data updated!", {})
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def add_company(company, user_id, db):
    """Creates a company and adds a branch to it"""
    # try:
    user_exists = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
    if user_exists is None:
        return ResponseDTO(404, "User does not exist!", {})

    new_company = Companies(company_name=company.company_name, owner=user_id, modified_by=user_id,
                            activity_status=company.activity_status)
    db.add(new_company)
    db.flush()

    add_company_to_ucb(new_company, user_id, db)

    branch = AddBranch
    branch.branch_name = company.branch_name
    branch.is_head_quarter = company.is_head_quarter
    init_branch = add_branch(branch, user_id, new_company.company_id, db, True)

    db.commit()

    return ResponseDTO(200, "Company created successfully",
                       AddCompanyResponse(company_name=new_company.company_name, company_id=new_company.company_id,
                                          branch=init_branch))


# except Exception as exc:
#     return ResponseDTO(204, str(exc), {})


def fetch_company(user_id, company_id, branch_id, db):
    """Fetches all companies owned by a user"""
    try:
        user_exists = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
        if user_exists is None:
            return ResponseDTO(404, "User does not exist!", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            existing_companies_query = db.query(Companies).filter(
                Companies.owner == user_id).all()

            existing_companies = [
                GetCompany(
                    company_id=company.company_id,
                    company_name=company.company_name,
                    owner=company.owner,
                    activity_status=company.activity_status
                )
                for company in existing_companies_query
            ]
            return ResponseDTO(200, "Companies fetched!", {"user_id": user_id, "companies": existing_companies})
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def modify_company(company, user_id, company_id, branch_id, comp_id, db):
    """Updates company data"""
    try:
        user_exists = db.query(UsersAuth).filter(UsersAuth.user_id == user_id).first()
        if user_exists is None:
            return ResponseDTO(404, "User does not exist!", {})

        check = check_if_company_and_branch_exist(company_id, branch_id, db)

        if check is None:
            company_query = db.query(Companies).filter(Companies.company_id == comp_id)
            if company_query.first() is None:
                return ResponseDTO(404, "The company to be updated does not exist!", {})

            company.modified_on = datetime.now()
            company.modified_by = user_id
            company.owner = user_id
            company.activity_status = company.activity_status
            company_query.update(company.__dict__)
            db.commit()

            return ResponseDTO(200, "Company data updated!", {})
        else:
            return check

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})


def get_all_user_data(ucb, db):
    try:
        company = db.query(Companies).filter(Companies.company_id == ucb.company_id).first()

        stmt = select(UserCompanyBranch.branch_id, UserCompanyBranch.designations,
                      UserCompanyBranch.accessible_features,
                      UserCompanyBranch.accessible_modules,
                      Branches.branch_name).select_from(UserCompanyBranch).join(
            Branches, UserCompanyBranch.branch_id == Branches.branch_id).filter(
            UserCompanyBranch.user_id == ucb.user_id)

        branches = db.execute(stmt)
        result = [
            UserDataResponse(
                branch_id=branch.branch_id,
                branch_name=branch.branch_name,
                designations=branch.designations,
                accessible_modules=branch.accessible_modules,
                accessible_features=branch.accessible_features
            )
            for branch in branches
        ]

        return GetUserDataResponse(company_id=company.company_id, company_name=company.company_name, branches=result)

    except Exception as exc:
        return ResponseDTO(204, str(exc), {})
