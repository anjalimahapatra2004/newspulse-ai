class AppError(Exception):
    """Base class for all expected, handled application errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DuplicateEmailError(AppError):
    def __init__(self, message="An account with this email already exists. Try logging in instead."):
        super().__init__(message, status_code=409)


class InvalidCredentialsError(AppError):
    def __init__(self, message="Incorrect password. Please try again."):
        super().__init__(message, status_code=401)


class UserNotFoundError(AppError):
    def __init__(self, message="No account found with this email."):
        super().__init__(message, status_code=404)


class ExpiredTokenError(AppError):
    def __init__(self, message="This link has expired. Please request a new one."):
        super().__init__(message, status_code=400)


class InvalidTokenError(AppError):
    def __init__(self, message="This link is invalid or has already been used."):
        super().__init__(message, status_code=400)


class EmailDeliveryError(AppError):
    def __init__(self, message="We couldn't send that email right now. Please try again shortly."):
        super().__init__(message, status_code=502)


class ExternalServiceError(AppError):
    """Raised when a third-party call (Groq, NewsAPI, etc.) fails."""
    def __init__(self, message="An external service is temporarily unavailable. Please try again."):
        super().__init__(message, status_code=503)