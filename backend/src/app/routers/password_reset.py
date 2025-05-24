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

# Define password-related API routes
router = APIRouter(
    prefix="/api/password",     # Route prefix
    tags=["password"]       # Route tag
)

# Step 1: Check if the email exists (frontend may use this as pre-check)
@router.post("/forgot-password")
def forgot_password(data: PasswordResetRequest, db: Session = Depends(get_session)):
    return verify_email(data.email, db)

# Step 2: Send verification code to the user's email
@router.post("/send-code")
def send_code(data: PasswordResetRequest, db: Session = Depends(get_session)):
    if send_verification_code(data.email, db):  # If sending is successful
        return {"msg": "Verification code sent (if the email exists)."}  # General response to avoid revealing if email exists
    else:
        raise HTTPException(status_code=404, detail="Email not found.")  # Email does not exist

# Step 3: Verify the code entered by the user
@router.post("/verify-code")
def verify_code_endpoint(data: CodeVerifyRequest, db: Session = Depends(get_session)):
    return verify_code(data.email, data.code, db)

# Step 4: Reset the password using a verified token
@router.post("/reset-password")
def reset_password_endpoint(data: PasswordResetConfirm, db: Session = Depends(get_session)):
    return reset_password(data.token, data.new_password, db)