from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserRequestAdd(BaseModel):
    login: str = Field(description="Уникальный псевдоним в качестве логина")
    email: str = Field(description="Адрес электронной почты")
    password: str = Field(description="Сырой пароль")


class UserAdd(BaseModel):
    login: str = Field(description="Уникальный псевдоним в качестве логина")
    email: str = Field(description="Адрес электронной почты")
    hashed_password: str = Field(description="Хэшированный пароль")
    email_verified: bool = Field(False, description="Флаг верификации адреса электронной почты")


class User(BaseModel):
    id: int = Field(description="Идентификатор пользователя")
    login: str = Field(description="Уникальный псевдоним в качестве логина")
    email: str = Field(description="Адрес электронной почты")
    email_verified: bool = Field(False, description="Флаг верификации адреса электронной почты")

    model_config = ConfigDict(from_attributes=True)


class UserWithHashedPassword(User):
    hashed_password: str = Field(description="Хэшированный пароль")


class UserAuthResponse(BaseModel):
    id: int = Field(description="Идентификатор пользователя")
    login: str = Field(description="Уникальный псевдоним в качестве логина")
    email_verified: bool = Field(False, description="Флаг верификации адреса электронной почты")


class AuthCheckResponse(BaseModel):
    authenticated: bool
    user: UserAuthResponse | None


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str


class UserLoginRequest(BaseModel):
    login: str = Field(description="Уникальный псевдоним в качестве логина")
    password: str = Field(description="Сырой пароль")


class UserRegisterRequest(UserLoginRequest):
    email: str = Field(description="Адрес электронной почты")
