from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.user import UserRead
from app.services.nsi_sync import sync_nsi

router = APIRouter(prefix="/admin", tags=["Администрирование"])


@router.get(
    "/users",
    response_model=list[UserRead],
    summary="Зеркало пользователей IdP (read-only)",
    dependencies=[Depends(require_admin)],
)
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.login).all()


@router.post(
    "/sync-nsi",
    summary="Синхронизировать НСИ из REPORTS-ASUBANK (Администратор)",
    dependencies=[Depends(require_admin)],
)
def trigger_nsi_sync(db: Session = Depends(get_db)):
    """Запрашивает валюты и счета ностро из REPORTS-ASUBANK и добавляет недостающие.
    Существующие данные и лимиты не перезаписываются."""
    return sync_nsi(db)


@router.get(
    "/audit",
    summary="Журнал аудита",
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
