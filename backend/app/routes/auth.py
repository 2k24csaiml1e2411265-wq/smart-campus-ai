from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import create_access_token, get_current_user, verify_password
from app.models.department import Department
from app.models.user import User
from app.schemas import LoginRequest, TokenResponse, UserOut
from app.utils.logging import logger

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if not user or not verify_password(body.password, user.password_hash):
        logger.info("auth_failed", email=body.email)
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user)
    dept = db.get(Department, user.department_id) if user.department_id else None
    return TokenResponse(
        access_token=token,
        role=user.role.value,
        email=user.email,
        department_code=dept.code if dept else None,
    )


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
