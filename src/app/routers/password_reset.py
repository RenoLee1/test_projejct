from fastapi import APIRouter, HTTPException, Depends
from app.schemas.password_reset import (
    PasswordResetRequest,
    PasswordResetConfirm,
    CodeVerifyRequest
)
from app.services.password_reset import (
    verify_email,
    reset_password,
    send_verification_code,
    verify_code
)
from app.database.session import get_session
from sqlmodel import Session

# 创建密码相关的API路由 | Define password-related API routes
router = APIRouter(
    prefix="/api/password",     # 路由前缀 | Route prefix
    tags=["password"]       # 路由分组标签 | Route tag
)

# 第一步：验证邮箱是否存在（前端可以调用该接口预检查）
# Step 1: Check if the email exists (frontend may use this as pre-check)
@router.post("/forgot-password")
def forgot_password(data: PasswordResetRequest, db: Session = Depends(get_session)):
    return verify_email(data.email, db)

# 第二步：发送验证码到邮箱
# Step 2: Send verification code to the user's email
@router.post("/send-code")
def send_code(data: PasswordResetRequest, db: Session = Depends(get_session)):
    if send_verification_code(data.email, db):  # 成功发送 | If sending is successful
        return {"msg": "Verification code sent (if the email exists)."}  # 提示统一格式，不暴露用户是否存在 | General response to avoid revealing if email exists
    else:
        raise HTTPException(status_code=404, detail="Email not found.")  # 邮箱不存在 | Email does not exist

# 第三步：校验用户输入的验证码
# Step 3: Verify the code entered by the user
@router.post("/verify-code")
def verify_code_endpoint(data: CodeVerifyRequest, db: Session = Depends(get_session)):
    return verify_code(data.email, data.code, db)

# 第四步：使用token重置密码
# Step 4: Reset the password using a verified token
@router.post("/reset-password")
def reset_password_endpoint(data: PasswordResetConfirm, db: Session = Depends(get_session)):
    return reset_password(data.token, data.new_password, db)