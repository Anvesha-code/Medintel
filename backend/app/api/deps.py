from fastapi import Header, HTTPException
from typing import Optional
from app.core.security import verify_jwt


def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Dependency to extract and verify JWT from Authorization header.
    Returns decoded JWT payload if valid.
    """

    # 1️⃣ Header missing
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    # 2️⃣ Wrong format
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format"
        )

    # 3️⃣ Extract token
    token = authorization.split(" ", 1)[1]

    # 4️⃣ Verify token
    payload = verify_jwt(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    # 5️⃣ Return JWT payload (contains `sub` = user_id)
    return payload
