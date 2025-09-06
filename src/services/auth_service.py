from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
from passlib.context import CryptContext
import jwt

# from src.api.dependencies import DBDep
from src.config import settings


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return AuthService.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return AuthService.pwd_context.hash(password)

    def create_access_token(self, user_data: dict) -> str:
        to_encode = user_data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode["exp"] = expire
        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": True},
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Токен истёк")
        except jwt.PyJWTError as e:
            raise HTTPException(status_code=401, detail=f"Неверный токен: {str(e)}")

    # @staticmethod
    # async def get_user(db: DBDep, user_id: int):
    #     user = await db.users.get_one_or_none(id=user_id)
    #     return user

    @staticmethod
    def create_password_reset_token(email: str) -> str:
        """Генерация JWT для сброса пароля (живёт 1 час)"""
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
        return jwt.encode(
            {"email": email, "exp": expire, "sub": "password_reset"},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def verify_password_reset_token(token: str) -> str:
        """Верификация токена сброса пароля"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"require_sub": "password_reset"}
            )
            return payload["email"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Ссылка сброса истекла")
        except jwt.PyJWTError:
            raise HTTPException(status_code=400, detail="Неверная ссылка сброса")
