from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException
from src.config import settings

from fastapi_mail import FastMail, MessageSchema, MessageType
from src.email_config import conf
from src.utils.logger import get_email_logger

logger = get_email_logger()


class EmailService:
    @staticmethod
    def create_email_token(email: str) -> str:
        """Генерация JWT для подтверждения email"""
        payload = {
            "email": email,
            "exp": datetime.now(timezone.utc) + timedelta(days=1),
            "sub": "email_verification"  # Добавляем тип токена
        }
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def verify_email_token(token: str) -> str:
        """Верификация токена подтверждения email"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"require_sub": "email_verification"}  # Проверяем тип
            )
            return payload["email"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=400,
                detail="Ссылка подтверждения истекла"
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=400,
                detail="Неверная ссылка подтверждения"
            )

    @staticmethod
    async def send_verification_email(email: str, username, token: str):
        verification_url = f"{settings.DOMAIN}api/v1/auth/verify-email?token={token}"

        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .button {{ 
                        display: inline-block; 
                        padding: 12px 24px; 
                        background-color: #007bff; 
                        color: white; 
                        text-decoration: none; 
                        border-radius: 5px; 
                        margin: 20px 0; 
                    }}
                    .footer {{ color: #666; font-size: 12px; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <p>{'Добро пожаловать, ' + username + '!' if username else 'Добро пожаловать!'}</p>

                <p>Благодарим за регистрацию в Forward Trading!</p>

                <p>Для завершения регистрации нажмите на кнопку:</p>

                <a href="{verification_url}" class="button">Подтвердить Email</a>

                <p>Или скопируйте ссылку в браузер:<br>
                <small>{verification_url}</small></p>

                <div class="footer">
                    <p><strong>Важно:</strong></p>
                    <ul>
                        <li>Ссылка действительна в течение 24 часов</li>
                        <li>Если вы не регистрировались, проигнорируйте это письмо</li>
                    </ul>
                    <p>С уважением,<br>Команда Forward Trading</p>
                </div>
            </body>
            </html>
            """

        fm = FastMail(conf)

        message = MessageSchema(
            subject="Подтверждение email для Forward Trading",
            recipients=[email],
            body=html_content,
            subtype=MessageType.html
        )

        try:
            await fm.send_message(message)
            logger.info(f"HTML письмо отправлено на {email}")
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки HTML письма: {e}")
            return False

    @staticmethod
    async def send_password_reset_email(email: str, token: str):
        reset_url = f"{settings.DOMAIN}api/v1/auth/password-reset/confirm?token={token}"

        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .button {{ 
                        display: inline-block; 
                        padding: 12px 24px; 
                        background-color: #007bff; 
                        color: white; 
                        text-decoration: none; 
                        border-radius: 5px; 
                        margin: 20px 0; 
                    }}
                    .footer {{ color: #666; font-size: 12px; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <p>'Здравствуйте!'</p>

                <p>На данный адрес получен запрос на сброс пароля</p>

                <p>Для сброса пароля нажмите на кнопку:</p>

                <a href="{reset_url}" class="button">Сбросить пароль</a>

                <p>Или скопируйте ссылку в браузер:<br>
                <small>{reset_url}</small></p>

                <div class="footer">
                    <p><strong>Важно:</strong></p>
                    <ul>
                        <li>Ссылка действительна в течение 1 часа</li>
                        <li>Если вы не запрашивали сброс пароля, проигнорируйте это письмо</li>
                    </ul>
                    <p>С уважением,<br>Команда Forward Trading</p>
                </div>
            </body>
            </html>
            """
        fm = FastMail(conf)

        message = MessageSchema(
            subject="Сброс пароля в Forward Trading",
            recipients=[email],
            body=html_content,
            subtype=MessageType.html
        )

        try:
            await fm.send_message(message)
            logger.info(f"HTML письмо отправлено на {email}")
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки HTML письма: {e}")
            return False
