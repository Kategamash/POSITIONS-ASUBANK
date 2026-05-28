"""Аутентификация через Identity Provider.

POSITIONS-АСУБАНК больше не хранит свою таблицу пользователей и не выдаёт
HS256-токены. Вход выполняется в общий Identity Provider (RS256 / JWKS),
а сервис только валидирует входящие user-токены.

Эндпоинт /auth/login оставлен как тонкий прокси к IdP, чтобы существующая
фронтенд-форма продолжала работать без изменений.
"""

from __future__ import annotations

import os

import httpx
from fastapi import APIRouter, HTTPException, Request, Response, status

from app.dependencies import CurrentUser

router = APIRouter(prefix="/auth", tags=["Авторизация"])

IDP_BASE_URL = os.getenv("IDP_BASE_URL", os.getenv("JWT_ISSUER", "http://185.17.3.75:8083"))


@router.post("/login", summary="Вход через Identity Provider")
async def login(body: dict, response: Response):
    email = body.get("email") or body.get("login")
    password = body.get("password") or body.get("пароль")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Укажите email и пароль")

    url = f"{IDP_BASE_URL.rstrip('/')}/api/v1/auth/login"
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            r = await client.post(url, json={"email": email, "password": password})
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"IdP недоступен: {exc}") from exc

    if r.status_code != 200:
        try:
            err = r.json()
        except Exception:  # noqa: BLE001
            err = {"detail": r.text or "Ошибка входа"}
        msg = err.get("message") or err.get("detail") or "Ошибка входа"
        raise HTTPException(status_code=r.status_code, detail=msg)

    payload = r.json()
    access = payload.get("accessToken") or payload.get("access_token")
    refresh = payload.get("refreshToken") or payload.get("refresh_token")
    if access:
        response.set_cookie("access_token", access, httponly=True, samesite="lax", max_age=14 * 60)
    if refresh:
        response.set_cookie("refresh_token", refresh, httponly=True, samesite="lax", max_age=25 * 86400)

    # Декодируем claims без проверки подписи (для UI; реальная валидация — на API).
    user_info: dict = {}
    if access:
        try:
            import jwt as _jwt

            claims = _jwt.decode(access, options={"verify_signature": False})
            first_name = claims.get("first_name") or claims.get("firstName")
            last_name = claims.get("last_name") or claims.get("lastName")
            email_claim = claims.get("email") or claims.get("sub")
            user_info = {
                "id": claims.get("user_id") or claims.get("sub"),
                "login": email_claim,
                "full_name": " ".join(p for p in (first_name, last_name) if p) or email_claim,
                "role": claims.get("role"),
                "is_active": True,
            }
        except Exception:  # noqa: BLE001
            user_info = {}

    return {
        "access_token": access,
        "token_type": "Bearer",
        "refresh_token": refresh,
        "user": user_info,
        # Сохраняем оригинальные поля для совместимости с другими клиентами.
        **payload,
    }


@router.post("/logout", summary="Очистить cookie сессии")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Выход выполнен успешно"}


@router.get("/me", summary="Текущий пользователь")
def me(current_user: CurrentUser):
    return {
        "id": current_user.id,
        "login": current_user.login,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }
