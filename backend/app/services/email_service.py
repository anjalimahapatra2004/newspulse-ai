from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.config import settings
from app.exceptions import EmailDeliveryError
from app.logger import get_logger

logger = get_logger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


async def _send(message: MessageSchema, context: str):
    try:
        await FastMail(conf).send_message(message)
        logger.info("Email sent (%s) to %s", context, message.recipients)
    except Exception:
        logger.error("Email send failed (%s) to %s", context, message.recipients, exc_info=True)
        raise EmailDeliveryError()


async def send_welcome_email(to_email: str, name: str):
    message = MessageSchema(
        subject="Welcome to NewsPulse AI",
        recipients=[to_email],
        body=f"""
        <h2>Welcome aboard, {name}!</h2>
        <p>Your NewsPulse AI account is ready. We'll start learning your interests
        as you read, and send you a personalized digest of Tech/AI and World news.</p>
        """,
        subtype=MessageType.html,
    )
    await _send(message, context="welcome")


async def send_reset_email(to_email: str, reset_link: str):
    message = MessageSchema(
        subject="Reset your NewsPulse AI password",
        recipients=[to_email],
        body=f"""
        <h2>Password reset requested</h2>
        <p>Click the link below to set a new password. This link expires in
        {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
        <p><a href="{reset_link}">Reset my password</a></p>
        <p>If you didn't request this, you can safely ignore this email.</p>
        """,
        subtype=MessageType.html,
    )
    await _send(message, context="password reset")


async def send_digest_email(to_email: str, name: str, tech_articles: list, world_articles: list):
    def render_section(title: str, articles: list) -> str:
        if not articles:
            return ""
        items = "".join(f"<li><a href='{a['url']}'>{a['title']}</a></li>" for a in articles)
        return f"<h3>{title}</h3><ul>{items}</ul>"

    body = f"""
    <h2>Your NewsPulse AI digest, {name}</h2>
    {render_section("Tech & AI", tech_articles)}
    {render_section("World", world_articles)}
    """
    message = MessageSchema(
        subject="Your NewsPulse AI digest",
        recipients=[to_email],
        body=body,
        subtype=MessageType.html,
    )
    await _send(message, context="digest")