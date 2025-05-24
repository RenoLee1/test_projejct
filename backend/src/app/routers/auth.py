from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session
from app.database.session import get_session
from app.schemas.user_schema import UserLogin, UserInfo,UserRegister
from app.schemas.user_approve_schema import UserApprovalUpdate,UserWithApproval,UserApprovalRead,RejectUserRequest,UserWithApprovalRead

from app.services.auth_service import authenticate_user, update_or_create_user_session_login_info,register_user,reject_user,read_user_approval,list_all_approvals,make_user_admin,fetch_user_approval_status,approve_user
from app.schemas.response import success, error, Response
from app.crud.user_crud import get_user_by_id, get_user_by_username, get_approval_by_user_id
from app.utils.auth_util import verify_password
from app.dependencies.auth import get_current_user 
from app.models.user_approve import UserApproval

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.get("/me", response_model=UserInfo, summary="Get current logged-in user info")
def get_current_user_info(current_user: UserInfo = Depends(get_current_user)):
    return current_user

def get_current_user_info(
    current: UserInfo = Depends(get_current_user)
) -> UserInfo:
    """
    If user is logged in, return { id, username, email, role };
    Otherwise return 401.
    """
    return current

@router.post("/login", response_model=Response[UserInfo])
def login(
        request: Request,
        login_data: UserLogin,
        db: Session = Depends(get_session)
):
    """
    User login, store user info in session
    """
    user, error_message = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        return error(code=401, message=error_message)

    # Update login information
    client_ip = request.client.host
    session = update_or_create_user_session_login_info(db, user, client_ip)

    # Store user info in session
    request.session["user_id"] = user.id
    request.session["role"] = user.role

    print("======Login======\n","id: ", user.id, "\nUsername: ", user.username,"\nRole: ", user.role ,"\n============")

    return success(data=UserInfo(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role
    ))

@router.post("/logout")
def logout(request: Request):
    """
    User logout
    """
    request.session.clear()
    return success(message="Logged out successfully")

@router.post("/register", response_model=Response[int])
def register(
        register_data: UserRegister,
        db: Session = Depends(get_session)
):
    """
    Register a new user account
    """
    # 1. Check if email or username already exists
    uid = register_user(db, register_data)

    return success(data=uid, message="Registration successful")

@router.post("/approve", response_model=Response[str])
def approve_user_endpoint(
    approval_data: UserApprovalUpdate,
    db: Session = Depends(get_session)
):
    try:
        approve_user(db, approval_data)
        return success(message="User has been approved successfully.")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
@router.post("/reject", response_model=Response[str])
def reject_user_endpoint(
    reject_data: RejectUserRequest,
    db: Session = Depends(get_session)
):
    reject_user(db, reject_data.user_id, reject_data.version, reject_data.comment,reject_data.is_cancel)
    return success(message="User has been rejected and notified by email.")

@router.get("/approval/{user_id}", response_model=Response[UserApproval])
def get_approval(user_id: int, db: Session = Depends(get_session)):
    approval = read_user_approval(db, user_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval record not found")

    return success(data=approval)

@router.get("/user/approveList", response_model=Response[list[UserWithApprovalRead]])
def get_user_approvals(db: Session = Depends(get_session)):
    data = list_all_approvals(db)

    result = [UserWithApprovalRead.from_orm(x) for x in data]

    return success(data=result)

@router.post("/promote", response_model=Response[str])
def promote_user(user_id: int, db: Session = Depends(get_session)):
    try:
        make_user_admin(db, user_id)
        return success(message="User promoted to admin successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/approval/status/{user_id}", response_model=Response[str])
def get_user_approval_status(user_id: int, db: Session = Depends(get_session)):
    try:
        status = fetch_user_approval_status(db, user_id)
        return success(data=status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/me")
def get_current_user(request: Request):
    """
    Get current logged-in user info from session
    """
    user_id = request.session.get("user_id")
    role = request.session.get("role")

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "id": user_id,
        "role": role,
    }