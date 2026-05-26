from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser, require_admin
from app.models.audit import AuditLog
from app.models.user import User, ROLES
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.auth_service import hash_password

router = APIRouter(prefix="/admin", tags=["Администрирование"])


@router.get(
    "/users",
    response_model=list[UserRead],
    summary="Список пользователей (Администратор)",
    dependencies=[Depends(require_admin)],
)
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя (Администратор)",
    dependencies=[Depends(require_admin)],
)
def create_user(body: UserCreate, request: Request, db: Session = Depends(get_db)):
    if body.role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Недопустимая роль. Доступны: {ROLES}")
    if db.query(User).filter(User.login == body.login).first():
        raise HTTPException(status_code=409, detail="Пользователь с таким логином уже существует")

    user = User(
        login=body.login,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
    )
    db.add(user)
    db.flush()

    db.add(AuditLog(
        user_id=user.id,
        login=user.login,
        action="USER_CREATED",
        entity="users",
        entity_id=str(user.id),
        details={"role": user.role, "full_name": user.full_name},
        ip_address=request.client.host if request.client else None,
    ))
    db.commit()
    db.refresh(user)
    return user


@router.patch(
    "/users/{user_id}",
    response_model=UserRead,
    summary="Изменить пользователя (Администратор)",
    dependencies=[Depends(require_admin)],
)
def update_user(
    user_id: UUID, body: UserUpdate, request: Request, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if body.role and body.role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Недопустимая роль. Доступны: {ROLES}")

    changes = {}
    for field, value in body.model_dump(exclude_none=True).items():
        if field == "password":
            user.password_hash = hash_password(value)
            changes["password"] = "changed"
        else:
            changes[field] = value
            setattr(user, field, value)

    db.add(AuditLog(
        user_id=user.id,
        login=user.login,
        action="USER_UPDATED",
        entity="users",
        entity_id=str(user.id),
        details=changes,
        ip_address=request.client.host if request.client else None,
    ))
    db.commit()
    db.refresh(user)
    return user


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Деактивировать пользователя (Администратор)",
    dependencies=[Depends(require_admin)],
)
def deactivate_user(user_id: UUID, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.is_active = False
    db.add(AuditLog(
        user_id=user.id,
        login=user.login,
        action="USER_DEACTIVATED",
        entity="users",
        entity_id=str(user.id),
        ip_address=request.client.host if request.client else None,
    ))
    db.commit()


@router.get(
    "/audit",
    summary="Журнал аудита (Администратор)",
    dependencies=[Depends(require_admin)],
)
def get_audit_log(
    login: str | None = None,
    action: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(AuditLog)
    if login:
        q = q.filter(AuditLog.login == login)
    if action:
        q = q.filter(AuditLog.action == action)
    return q.order_by(AuditLog.created_at.desc()).limit(500).all()
