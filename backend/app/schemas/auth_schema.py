from pydantic import BaseModel, EmailStr, Field


class SignupSchema(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class GoogleAuthSchema(BaseModel):
    id_token: str


class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    name: str
    email: EmailStr


class MessageResponse(BaseModel):
    message: str