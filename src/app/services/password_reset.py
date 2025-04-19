import secrets
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlmodel import Session
from passlib.hash import bcrypt  # 引入密码哈希函数 / Import password hashing function

from app.crud.user_crud import get_user_by_email
from app.utils.email_sender import EmailSender

# 内存缓存，用于存储验证码或 token 及其过期时间
# In-memory cache to store verification codes or tokens with expiry
reset_code_cache = {}

# 验证邮箱是否已注册
# Verify if email is already registered
def verify_email(email: str, db: Session) -> bool:
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")
    return True

# 生成安全随机 token
# Generate a secure random token
def generate_token():
    return secrets.token_urlsafe(32)

# 生成 6 位验证码（补零）
# Generate a 6-digit verification code (zero-padded)
def generate_code():
    return f"{secrets.randbelow(1000000):06d}"

# 发送验证码并缓存
# Send verification code and store it in the cache
def send_verification_code(email: str, db: Session) -> bool:
    user = get_user_by_email(db, email)
    if not user:
        return False

    code = generate_code()
    expiry = datetime.now(timezone.utc) + timedelta(minutes=30)
    reset_code_cache[email] = (code, expiry)
    print("reset code", reset_code_cache[email])

    sender = EmailSender(
        smtp_server="smtp.qq.com",
        smtp_port=587,
        username="2602449682@qq.com",
        password="qdeprcpfakyceaaa"
    )
    sender.send_email(
        to=email,
        subject="Your Verification Code",
        body=f"Your verification code is: {code}\nIt is valid for 30 minutes. Please do not share it."
    )
    return True

# 验证验证码是否有效
# Verify if the provided code is valid
def verify_code(email: str, code: str, db: Session):
    if email not in reset_code_cache:
        raise HTTPException(status_code=400, detail="No verification code found")

    stored_code, expiry = reset_code_cache[email]
    if stored_code != code:
        raise HTTPException(status_code=400, detail="Invalid code")
    if datetime.now(timezone.utc) > expiry:
        raise HTTPException(status_code=400, detail="Code expired")

    token = generate_token()
    print("token: ", token)
    reset_code_cache[email] = (token, datetime.now(timezone.utc) + timedelta(minutes=30))
    return {"msg": "Code verified", "token": token}

# 使用 token 重置密码（已集成加密）
# Reset password using token (with encryption)
def reset_password(token: str, new_password: str, db: Session):
    matched_email = None
    for email, (stored_token, expiry) in reset_code_cache.items():
        if stored_token == token and expiry > datetime.now(timezone.utc):
            matched_email = email
            break

    if not matched_email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = get_user_by_email(db, matched_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 哈希新密码
    # Hash the new password before saving
    user.password = bcrypt.hash(new_password)

    db.add(user)
    db.commit()
    del reset_code_cache[matched_email]

    return {"msg": "Password reset successful"}
