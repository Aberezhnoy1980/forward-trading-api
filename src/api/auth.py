from fastapi import APIRouter, HTTPException, Body
from fastapi import BackgroundTasks

from src.schemas.users import UserAdd, UserRegisterRequest
from src.services.auth_service import AuthService
from src.services.email_service import EmailService
from src.api.dependencies import DBDep

from src.utils.openapi_examples import user_examples
from src.utils.logger import get_auth_logger

logger = get_auth_logger()

router = APIRouter(prefix="/v1/auth", tags=["Авторизация и аутентификация"])


@router.post(
    "/register",
    summary="Регистрация нового пользователя",
    description="<h3>Добавляет запись данных пользователя в базу данных</h3>",
)
async def register(
        db: DBDep,
        background_tasks: BackgroundTasks,
        user_data: UserRegisterRequest = Body(openapi_examples=user_examples),
):
    """
    Регистрация нового пользователя
    - Сохраняет пользователя с email_verified=False
    - Генерирует токен подтверждения
    - Отправляет письмо со ссылкой для подтверждения
    """

    # Нормализация email
    email = user_data.email.strip().lower()

    # Проверка уникальности
    if await db.users.email_exists(email):
        raise HTTPException(status_code=409, detail="Email уже занят")
    if await db.users.login_exists(user_data.login):
        raise HTTPException(status_code=409, detail="Логин уже занят")

    # Хешируем только пароль
    hashed_password = AuthService().hash_password(user_data.password)

    # Сохраняем пользователя (email хранится как есть)
    new_user = UserAdd(
        login=user_data.login,
        email=email,
        hashed_password=hashed_password,
        email_verified=False
    )

    await db.users.add(new_user)
    await db.commit()

    # 3. Генерируем токен подтверждения
    verify_token = EmailService().create_email_token(user_data.email)

    # 4. Отправляем письмо
    background_tasks.add_task(
        EmailService.send_verification_email,
        user_data.email, user_data.login,
        verify_token  # Отправляем токен, а не хеш
    )

    return {"status": "ok", "message": "Письмо с подтверждением отправлено"}


@router.get("/verify-email")
async def verify_email(db: DBDep, token: str):
    """
    Подтверждение email по токену
    - Проверяет токен
    - Обновляет email_verified=True в БД
    """
    email = EmailService.verify_email_token(token)

    await db.users.verify_email(email)
    await db.commit()

    return {"status": "ok", "message": "Email подтверждён"}
