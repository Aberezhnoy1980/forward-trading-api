from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request

from src.schemas.users import UserAuthResponse
from src.services.auth_service import AuthService
from src.utils.db_manager import DBManager
from src.users_db import async_session_maker


async def get_db():
    # async with get_db_manager() as db:
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


def get_token(request: Request) -> str:
    token = request.cookies.get("ft_access_token", None)
    if not token:
        raise HTTPException(status_code=401, detail="Токен не предоставлен")
    return token


def get_current_user_id(token: str = Depends(get_token)) -> int:
    try:
        data = AuthService().decode_token(token)
        return data["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истёк")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Неверный токен")


async def get_current_user(db: DBDep, user_id: int = Depends(get_current_user_id)) -> dict:
    """Зависимость для проверки JWT и подписки."""
    # Проверяем, что пользователь существует в БД
    user = await db.users.get_one_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user  # Возвращаем данные из токена


UserDep = Annotated[UserAuthResponse, Depends(get_current_user)]
