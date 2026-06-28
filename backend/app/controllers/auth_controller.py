import secrets
from datetime import datetime, timedelta, timezone
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from app.database import users_collection
from app.models.user_model import UserModel
from app.schemas.auth_schema import SignupSchema, LoginSchema, ForgotPasswordSchema, ResetPasswordSchema
from app.utils.security import hash_password, verify_password, create_access_token, generate_reset_token
from app.services.email_service import send_welcome_email, send_reset_email
from app.exceptions import DuplicateEmailError, InvalidCredentialsError, UserNotFoundError, ExpiredTokenError, InvalidTokenError
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)


async def signup_user(data: SignupSchema) -> dict:
    existing = await users_collection.find_one({"email": data.email.lower()})
    if existing:
        logger.warning("Signup blocked - email already exists: %s", data.email)
        raise DuplicateEmailError()

    user = UserModel(email=data.email, hashed_password=hash_password(data.password), name=data.name)
    await users_collection.insert_one(user.to_dict())
    logger.info("New user created: %s", user.email)

    try:
        await send_welcome_email(user.email, user.name)
    except Exception:
        # Don't fail signup just because the welcome email didn't send
        logger.error("Welcome email failed for %s", user.email, exc_info=True)

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "name": user.name, "email": user.email}


async def login_user(data: LoginSchema) -> dict:
    user = await users_collection.find_one({"email": data.email.lower()})
    if not user:
        logger.info("Login attempt for unknown email: %s", data.email)
        raise UserNotFoundError()

    if not verify_password(data.password, user["hashed_password"]):
        logger.warning("Failed login (wrong password) for: %s", data.email)
        raise InvalidCredentialsError()

    logger.info("Successful login: %s", user["email"])
    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer", "name": user["name"], "email": user["email"]}


async def forgot_password(data: ForgotPasswordSchema) -> dict:
    user = await users_collection.find_one({"email": data.email.lower()})
    generic_response = {"message": "If an account exists for this email, a reset link has been sent."}

    if not user:
        # Don't reveal whether the email exists - same response either way
        logger.info("Forgot-password request for unknown email: %s", data.email)
        return generic_response

    reset_token = generate_reset_token()
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    await users_collection.update_one(
        {"email": user["email"]},
        {"$set": {"reset_token": reset_token, "reset_token_expires": expires}},
    )

    reset_link = f"{settings.FRONTEND_URL}/reset-password.html?token={reset_token}"
    try:
        await send_reset_email(user["email"], reset_link)
        logger.info("Password reset email sent to: %s", user["email"])
    except Exception:
        logger.error("Reset email failed for %s", user["email"], exc_info=True)

    return generic_response


async def reset_password(data: ResetPasswordSchema) -> dict:
    user = await users_collection.find_one({"reset_token": data.token})
    if not user:
        logger.warning("Reset attempted with invalid/unknown token")
        raise InvalidTokenError()

    expires = user.get("reset_token_expires")
    if expires and expires.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        logger.warning("Reset attempted with expired token for: %s", user["email"])
        raise ExpiredTokenError()

    await users_collection.update_one(
        {"email": user["email"]},
        {
            "$set": {"hashed_password": hash_password(data.new_password)},
            "$unset": {"reset_token": "", "reset_token_expires": ""},
        },
    )
    logger.info("Password reset successfully for: %s", user["email"])
    return {"message": "Password updated successfully. You can now log in."}


async def google_login(token: str) -> dict:
    """Verifies a Google ID token server-side, then finds or creates the user."""
    try:
        idinfo = google_id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
    except ValueError:
        logger.warning("Invalid Google ID token rejected during sign-in")
        raise InvalidTokenError("Google sign-in failed. Please try again.")

    email = idinfo.get("email", "").lower()
    name = idinfo.get("name") or email.split("@")[0]

    user = await users_collection.find_one({"email": email})
    if not user:
        # Google-authenticated users get an unusable random password hash -
        # they can never log in via the password form unless they later set one.
        placeholder_password = hash_password(secrets.token_urlsafe(32))
        new_user = UserModel(email=email, hashed_password=placeholder_password, name=name, is_verified=True)
        await users_collection.insert_one(new_user.to_dict())
        logger.info("New user created via Google sign-in: %s", email)

        try:
            await send_welcome_email(new_user.email, new_user.name)
        except Exception:
            logger.error("Welcome email failed for Google signup %s", email, exc_info=True)

        final_email, final_name = new_user.email, new_user.name
    else:
        final_email, final_name = user["email"], user["name"]
        logger.info("Existing user logged in via Google: %s", email)

    access_token = create_access_token({"sub": final_email})
    return {"access_token": access_token, "token_type": "bearer", "name": final_name, "email": final_email}