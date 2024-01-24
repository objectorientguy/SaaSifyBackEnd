"""Service layer for Leaves"""
from datetime import datetime

from sqlalchemy import select

from app.v2_0.application.dto.dto_classes import ResponseDTO, ExceptionDTO
from app.v2_0.domain import models
from app.v2_0.domain.models import LeaveType
from app.v2_0.domain.schema import ApplyLeaveResponse, LoadApplyLeaveScreen, GetLeaves, GetPendingLeaves


def get_screen_apply_leave(user_id, company_id, branch_id, db):
    try:
        user = db.query(models.UserDetails).filter(models.UserDetails.user_id == user_id).first()
        ucb_user = db.query(models.UserCompanyBranch).filter(models.UserCompanyBranch.user_id == user_id).first()
        result = LoadApplyLeaveScreen(casual_leaves=user.casual_leaves, medical_leaves=user.medical_leaves,
                                      approvers=ucb_user.approvers)
        return ResponseDTO(200, "Data loaded!", result)
    except Exception as exc:
        return ExceptionDTO("get_screen_apply_leave", exc)


def check_remaining_leaves(user_id, leave_application, db):
    user = db.query(models.UserDetails).filter(models.UserDetails.user_id == user_id).first()
    if leave_application.leave_type == LeaveType.CASUAL and user.casual_leaves == 0:
        return 0
    if leave_application.leave_type == LeaveType.MEDICAL and user.medical_leaves == 0:
        return 1
    return 2


def apply_for_leave(leave_application, user_id, company_id, branch_id, db):
    try:
        message = check_remaining_leaves(user_id, leave_application, db)
        if message == 0:
            return ResponseDTO(200, "You have exhausted your casual leaves!", {})
        elif message == 1:
            return ResponseDTO(200, "You have exhausted your medical leaves!", {})
        else:
            leave_application.modified_by = user_id
            leave_application.user_id = user_id
            leave_application.company_id = company_id
            leave_application.branch_id = branch_id

            if len(leave_application.approvers) == 0:
                company = db.query(models.Companies).filter(models.Companies.company_id == company_id).first()
                leave_application.approvers = [company.owner]

            new_leave_application = models.Leaves(**leave_application.model_dump())
            db.add(new_leave_application)
            db.commit()
            db.refresh(new_leave_application)

            return ResponseDTO(200, "Leave application submitted",
                               ApplyLeaveResponse(leave_id=new_leave_application.leave_id,
                                                  leave_status=new_leave_application.leave_status,
                                                  is_leave_approved=new_leave_application.is_leave_approved,
                                                  comment=new_leave_application.comment))

    except Exception as exc:
        return ExceptionDTO("apply_for_leave", exc)


def fetch_leaves(user_id, company_id, branch_id, db):
    try:
        my_leaves = db.query(models.Leaves).filter(models.Leaves.user_id == user_id).all()
        result = [
            GetLeaves(company_id=leave.company_id, branch_id=leave.branch_id, user_id=leave.user_id,
                      leave_type=leave.leave_type, leave_id=leave.leave_id, leave_reason=leave.leave_reason,
                      start_date=leave.start_date, end_date=leave.end_date, approvers=leave.approvers,
                      leave_status=leave.leave_status)
            for leave in my_leaves
        ]
        if len(my_leaves) == 0:
            return ResponseDTO(204, "No leaves to fetch!", my_leaves)

        return ResponseDTO(200, "Leaves fetched!", result)
    except Exception as exc:
        return ExceptionDTO("fetch_leaves", exc)


def get_authorized_leave_requests(pending_leaves, user_id):
    try:
        filtered_leaves = []
        for x in pending_leaves:
            if user_id in x.__dict__["approvers"]:
                filtered_leaves.append(x)
        return filtered_leaves
    except Exception as exc:
        return ExceptionDTO("get_authorized_leave_requests", exc)


def format_pending_leaves(filtered_leaves, db):
    for x in filtered_leaves:
        user = db.query(models.UserDetails).filter(models.UserDetails.user_id == x.__dict__["user_id"]).first()
        x.__dict__["name"] = user.first_name + " " + user.last_name
    return filtered_leaves


def fetch_pending_leaves(user_id, company_id, branch_id, db):
    try:
        pending_leaves = db.query(models.Leaves).filter(models.Leaves.leave_status == "PENDING").all()
        if len(pending_leaves) == 0:
            return ResponseDTO(204, "No leaves to fetch!", pending_leaves)

        filter_leaves_by_approver = get_authorized_leave_requests(pending_leaves, user_id)

        if len(filter_leaves_by_approver) == 0:
            return ResponseDTO(204, "You are not authorized to view pending leaves", [])
        else:
            final_list = format_pending_leaves(filter_leaves_by_approver, db)
            result = [GetPendingLeaves(leave_id=item.leave_id, user_id=item.user_id, name=item.name,
                                       leave_type=item.leave_type, leave_reason=item.leave_reason,
                                       start_date=item.start_date, end_date=item.end_date, approvers=item.approvers)
                      for item in final_list
                      ]
        return ResponseDTO(200,"Leaves fetched!",result)

    except Exception as exc:
        return ExceptionDTO("fetch_pending_leaves", exc)


def update_user_leaves(leave, db):
    """Updates the number of leaves of an employee"""
    try:
        user_query = db.query(models.UserDetails).filter(models.UserDetails.user_id == leave.user_id)
        user = user_query.first()
        if leave.leave_type == LeaveType.CASUAL:
            user.casual_leaves = user.casual_leaves - 1
            user_query.update(casual_leaves=user.casual_leaves)
            db.commit()
        else:
            user.medical_leaves = user.medical_leaves - 1
            user_query.update(medical_leaves=user.medical_leaves)
            db.commit()

    except Exception as exc:
        return ExceptionDTO("update_user_leaves", exc)


def modify_leave_status(application_response, user_id, company_id, branch_id, db):
    """Leaves are ACCEPTED or REJECTED using this API"""
    try:
        leave_query = db.query(models.Leaves).filter(models.Leaves.leave_id == application_response.leave_id)
        leave = leave_query.first()
        status = "REJECTED"
        if leave is None:
            return ResponseDTO(404, "Leave entry not found!", {})
        if application_response.is_leave_approved is True:
            status = "ACCEPTED"
            update_user_leaves(leave, db)

        application_response.leave_status = status
        application_response.modified_by = user_id
        leave_query.update(application_response.__dict__)
        db.commit()

        return ResponseDTO(200, "Leave status updated!", {})
    except Exception as exc:
        return ExceptionDTO("modify_leave_status", exc)
