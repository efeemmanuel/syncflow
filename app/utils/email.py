from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_SERVER=settings.mail_server,
    MAIL_PORT=settings.mail_port,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

async def send_otp_email(email: str, otp: str):
    message = MessageSchema(
        subject="Verify your account",
        recipients=[email],
        body=f"Your verification code is: {otp}",
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)



async def send_admin_invite_email(email: str, token: str, company_name: str):
    message = MessageSchema(
        subject="You have been invited to join your company workspace",
        recipients=[email],
        body=f"You have been invited to manage {company_name}. Click the link to set up your account: http://localhost:8000/auth/accept-invite?token={token}",
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)




async def send_invite_email(email: str, token: str, role: str):
    message = MessageSchema(
        subject=f"You have been invited as {role}",
        recipients=[email],
        body=f"Click the link to set up your account: http://localhost:8000/auth/accept-invite?token={token}",
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)


