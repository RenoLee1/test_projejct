from pydantic import BaseModel, EmailStr

# Request body for sending password reset verification code
class PasswordResetRequest(BaseModel):
    email: EmailStr  # 用户邮箱 | User's email address

# Request body for verifying the code
class CodeVerifyRequest(BaseModel):
    email: EmailStr  # 用户邮箱 | User's email address
    code: str        # 用户收到的验证码 | Verification code sent to the user

# Request body for confirming the password reset
class PasswordResetConfirm(BaseModel):
    token: str           # Token generated after successful code verification
    new_password: str    # New password to be set by the user