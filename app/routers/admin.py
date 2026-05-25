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
    if body.роль not in ROLES:
        raise HTTPException(status_code=400, detail=f"Недопустимая роль. Доступны: {ROLES}")
    if db.query(User).filter(User.логин == body.логин).first():
        raise HTTPException(status_code=409, detail="Пользователь с таким логином уже существует")

    user = User(
        логин=body.логин,
        хэш_пароля=hash_password(body.пароль),
        полное_имя=body.полное_имя,
        роль=body.роль,
    )
    db.add(user)
    db.flush()

    db.add(AuditLog(
        пользователь_id=user.id,
        логин=user.логин,
        действие="USER_CREATED",
        сущность="пользователи",
        сущность_id=str(user.id),
        детали={"роль": user.роль, "полное_имя": user.полное_имя},
        ip_адрес=request.client.host if request.client else None,
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
    if body.роль and body.роль not in ROLES:
        raise HTTPException(status_code=400, detail=f"Недопустимая роль. Доступны: {ROLES}")

    changes = {}
    for field, value in body.model_dump(exclude_none=True).items():
        if field == "пароль":
            user.хэш_пароля = hash_password(value)
            changes["пароль"] = "изменён"
        else:
            changes[field] = value
            setattr(user, field, value)

    db.add(AuditLog(
        пользователь_id=user.id,
        логин=user.логин,
        действие="USER_UPDATED",
        сущность="пользователи",
        сущность_id=str(user.id),
        детали=changes,
        ip_адрес=request.client.host if request.client else None,
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
    user.активен = False
    db.add(AuditLog(
        пользователь_id=user.id,
        логин=user.логин,
        действие="USER_DEACTIVATED",
        сущность="пользователи",
        сущность_id=str(user.id),
        ip_адрес=request.client.host if request.client else None,
    ))
    db.commit()


@router.get(
    "/audit",
    summary="Журнал аудита (Администратор)",
    dependencies=[Depends(require_admin)],
)
def get_audit_log(
    логин: str | None = None,
    действие: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(AuditLog)
    if логин:
        q = q.filter(AuditLog.логин == логин)
    if действие:
        q = q.filter(AuditLog.действие == действие)
    return q.order_by(AuditLog.дата_время.desc()).limit(500).all()
