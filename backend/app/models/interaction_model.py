from datetime import datetime, timezone


class InteractionModel:
    """Logs a single user-article interaction (click, like, read)."""

    ACTION_WEIGHTS = {"click": 1, "like": 2, "read": 3}

    def __init__(self, user_id: str, article_id: str, action: str, created_at: datetime = None):
        self.user_id = user_id
        self.article_id = article_id
        self.action = action  # "click" | "like" | "read"
        self.weight = self.ACTION_WEIGHTS.get(action, 1)
        self.created_at = created_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "article_id": self.article_id,
            "action": self.action,
            "weight": self.weight,
            "created_at": self.created_at,
        }