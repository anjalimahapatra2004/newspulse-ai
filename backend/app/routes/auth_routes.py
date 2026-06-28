from fastapi import APIRouter
from app.schemas.auth_schema import (
    SignupSchema, LoginSchema, ForgotPasswordSchema, ResetPasswordSchema, GoogleAuthSchema,
    TokenResponse, MessageResponse,
)
from app.controllers import auth_controller

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/signup", response_model=TokenResponse)
async def signup(data: SignupSchema):
    return await auth_controller.signup_user(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginSchema):
    return await auth_controller.login_user(data)


@router.post("/google", response_model=TokenResponse)
async def google_signin(data: GoogleAuthSchema):
    return await auth_controller.google_login(data.id_token)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPasswordSchema):
    return await auth_controller.forgot_password(data)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPasswordSchema):
    return await auth_controller.reset_password(data)