import os
from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from ninja.security import HttpBearer

User = get_user_model()

SECRET_KEY = getattr(settings, "SECRET_KEY", "dev-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def create_access_token(user_id: int) -> str:
    """Создать JWT токен для пользователя."""
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """Декодировать токен, вернуть user_id или None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("sub"))
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


class JWTAuth(HttpBearer):
    """JWT аутентификация для Django Ninja."""

    async def authenticate(self, request, token: str):
        user_id = decode_access_token(token)
        if user_id is None:
            return None

        try:
            user = await User.objects.aget(id=user_id)
            return user
        except User.DoesNotExist:
            return None


class OptionalJWTAuth(HttpBearer):
    """Опциональная JWT аутентификация (не требует токен)."""

    async def authenticate(self, request, token: str | None):
        if not token:
            return None

        user_id = decode_access_token(token)
        if user_id is None:
            return None

        try:
            return await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            return None
