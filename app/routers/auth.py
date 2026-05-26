from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit import AuditLog
from app.schemas.user import LoginRequest, TokenResponse, UserRead
from app.services.auth_service import authenticate_user, create_access_token
from app.dependencies import CurrentUser

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/login", response_model=TokenResponse, summary="Вход в систему")
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = authenticate_user(db, body.login, body.password)
    if not user:
        db.add(AuditLog(
            login=body.login,
            action="LOGIN_FAILED",
            details={"reason": "Неверный логин или пароль"},
            ip_address=request.client.host if request.client else None,
        ))
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )

    token = create_access_token({"sub": str(user.id), "role": user.role})

    db.add(AuditLog(
        user_id=user.id,
        login=user.login,
        action="LOGIN",
        ip_address=request.client.host if request.client else None,
    ))
    db.commit()

    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@router.post("/logout", summary="Выход из системы")
def logout(current_user: CurrentUser, request: Request, db: Session = Depends(get_db)):
    db.add(AuditLog(
        user_id=current_user.id,
        login=current_user.login,
        action="LOGOUT",
        ip_address=request.client.host if request.client else None,
    ))
    db.commit()
    return {"detail": "Выход выполнен успешно"}


@router.get("/me", response_model=UserRead, summary="Текущий пользователь")
def me(current_user: CurrentUser):
    return current_user
