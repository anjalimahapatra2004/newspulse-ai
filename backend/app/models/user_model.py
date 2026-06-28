from datetime import datetime, timezone
from typing import Optional


class UserModel:
    """Represents a user document stored in MongoDB."""

    def __init__(
        self,
        email: str,
        hashed_password: str,
        name: str,
        preferences: Optional[list] = None,
        is_verified: bool = False,
        reset_token: Optional[str] = None,
        reset_token_expires: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ):
        self.email = email.lower().strip()
        self.hashed_password = hashed_password
        self.name = name
        # e.g. ["tech", "world"]
        self.preferences = preferences or ["tech", "world"]
        self.is_verified = is_verified
        self.reset_token = reset_token
        self.reset_token_expires = reset_token_expires
        self.created_at = created_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "email": self.email,
            "hashed_password": self.hashed_password,
            "name": self.name,
            "preferences": self.preferences,
            "is_verified": self.is_verified,
            "reset_token": self.reset_token,
            "reset_token_expires": self.reset_token_expires,
            "created_at": self.created_at,
        }