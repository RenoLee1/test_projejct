from pydantic import BaseModel, EmailStr

# 请求发送重置密码验证码时的请求体
# Request body for sending password reset verification code
class PasswordResetRequest(BaseModel):
    email: EmailStr  # 用户邮箱 | User's email address

# 请求验证验证码时的请求体
# Request body for verifying the code
class CodeVerifyRequest(BaseModel):
    email: EmailStr  # 用户邮箱 | User's email address
    code: str        # 用户收到的验证码 | Verification code sent to the user

# 请求确认密码重置时的请求体
# Request body for confirming the password reset
class PasswordResetConfirm(BaseModel):
    token: str           # 成功验证验证码后生成的token | Token generated after successful code verification
    new_password: str    # 用户设置的新密码 | New password to be set by the user