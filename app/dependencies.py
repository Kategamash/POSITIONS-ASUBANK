from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

ROLE_TRADER = "TRADER"
ROLE_POSITIONER = "POSITIONER"
ROLE_AUDITOR = "AUDITOR"
ROLE_ADMIN = "ADMIN"

log = logging.getLogger(__name__)

JWT_ISSUER = os.getenv("JWT_ISSUER", "http://identity-provider:8083")
JWKS_URL = os.getenv("JWKS_URL", f"{JWT_ISSUER}/.well-known/jwks.json")

bearer_scheme = HTTPBearer(auto_error=False)

_jwks: PyJWKClient | None = None


def _jwks_client() -> PyJWKClient:
    global _jwks
    if _jwks is None:
        _jwks = PyJWKClient(JWKS_URL, cache_keys=True)
    return _jwks


@dataclass(frozen=True)
class IdPUser:
    id: str
    login: str
    full_name: str
    role: str
    is_active: bool = True

    @property
    def email(self) -> str:
        return self.login


@dataclass(frozen=True)
class ServicePrincipal:
    client_id: str
    service: str
    scopes: tuple[str, ...]


def _decode(token: str) -> dict:
    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=JWT_ISSUER,
            options={"require": ["sub", "iss", "exp", "iat", "jti", "token_type"]},
        )
    except jwt.PyJWTError as exc:
        log.warning("JWT validation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def _extract_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
) -> str:
    if credentials and credentials.credentials:
        return credentials.credentials
    cookie = request.cookies.get("access_token")
    if cookie:
        return cookie
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Отсутствует токен доступа",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
    db: Session = Depends(get_db),
) -> IdPUser:
    token = _extract_token(request, credentials)
    claims = _decode(token)
    if claims.get("token_type") != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется пользовательский токен",
        )
    role = str(claims.get("role") or "AUDITOR").upper()
    if role not in (ROLE_TRADER, ROLE_POSITIONER, ROLE_AUDITOR, ROLE_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Неизвестная роль: {role}",
        )
    email = str(claims.get("email") or claims.get("sub"))
    full_name = " ".join(
        part for part in (claims.get("first_name"), claims.get("last_name")) if part
    ) or email
    user_id = str(claims.get("user_id") or claims["sub"])

    # Зеркалим IdP-пользователя в локальной БД для FK на audit/corrections.
    try:
        record = db.query(User).filter(User.id == user_id).first()
        changed = False
        if record is None:
            record = User(id=user_id, login=email, full_name=full_name, role=role, is_active=True)
            db.add(record)
            changed = True
        else:
            if record.login != email:
                record.login = email
                changed = True
            if record.full_name != full_name:
                record.full_name = full_name
                changed = True
            if record.role != role:
                record.role = role
                changed = True
            if not record.is_active:
                record.is_active = True
                changed = True
        if changed:
            db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()
        log.exception("Не удалось синхронизировать IdP-пользователя в локальной БД")

    return IdPUser(id=user_id, login=email, full_name=full_name, role=role)


CurrentUser = Annotated[IdPUser, Depends(get_current_user)]


def get_service_principal(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
) -> ServicePrincipal:
    token = _extract_token(request, credentials)
    claims = _decode(token)
    if claims.get("token_type") != "service":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется сервисный токен",
        )

    raw_scope = claims.get("scope") or []
    if isinstance(raw_scope, str):
        scopes = tuple(part for part in raw_scope.split() if part)
    elif isinstance(raw_scope, list):
        scopes = tuple(str(part) for part in raw_scope)
    else:
        scopes = ()

    return ServicePrincipal(
        client_id=str(claims.get("client_id") or claims.get("sub")),
        service=str(claims.get("service") or claims.get("client_id") or claims.get("sub")),
        scopes=scopes,
    )


def require_service_scope(*required_scopes: str):
    def checker(service: Annotated[ServicePrincipal, Depends(get_service_principal)]):
        missing = [scope for scope in required_scopes if scope not in service.scopes]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав сервисного токена: {', '.join(missing)}",
            )
        return service

    return checker


def require_user_or_service_scope(*allowed_service_scopes: str):
    def checker(
        request: Request,
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
    ):
        token = _extract_token(request, credentials)
        claims = _decode(token)
        token_type = claims.get("token_type")
        if token_type == "user":
            return claims
        if token_type != "service":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Требуется пользовательский или сервисный токен",
            )

        raw_scope = claims.get("scope") or []
        if isinstance(raw_scope, str):
            scopes = {part for part in raw_scope.split() if part}
        elif isinstance(raw_scope, list):
            scopes = {str(part) for part in raw_scope}
        else:
            scopes = set()
        if allowed_service_scopes and scopes.isdisjoint(set(allowed_service_scopes)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав сервисного токена: {', '.join(allowed_service_scopes)}",
            )
        return ServicePrincipal(
            client_id=str(claims.get("client_id") or claims.get("sub")),
            service=str(claims.get("service") or claims.get("client_id") or claims.get("sub")),
            scopes=tuple(sorted(scopes)),
        )

    return checker


def require_role(*roles: str):
    def checker(user: CurrentUser):
        if user.role == ROLE_ADMIN or user.role in roles:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Доступ запрещён. Требуется роль: {', '.join(roles)}",
        )

    return checker


def require_positioner_or_admin(user: CurrentUser):
    if user.role in (ROLE_POSITIONER, ROLE_ADMIN):
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Доступ запрещён. Требуется роль: Позиционер или Администратор",
    )


def require_admin(user: CurrentUser):
    if user.role == ROLE_ADMIN:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Доступ запрещён. Требуется роль: Администратор",
    )
