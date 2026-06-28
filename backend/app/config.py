from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "newspulse_ai"

    # JWT
    JWT_SECRET_KEY: str = "change-this"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # Groq
    GROQ_API_KEY: str = ""

    # Google OAuth (Sign in with Google)
    GOOGLE_CLIENT_ID: str = ""

    # Email
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "NewsPulse AI"

    # News ingestion
    NEWS_API_KEY: str = ""

    # Frontend
    FRONTEND_URL: str = "http://127.0.0.1:5500"

    # CORS - comma-separated list of allowed origins, e.g.
    # "http://127.0.0.1:5500,https://your-app.netlify.app"
    ALLOWED_ORIGINS: str = "http://127.0.0.1:5500"

    class Config:
        env_file = ".env"


settings = Settings()