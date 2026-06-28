from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

try:
    client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[settings.MONGO_DB_NAME]
    logger.info("MongoDB client created for database: %s", settings.MONGO_DB_NAME)
except Exception:
    logger.critical("Failed to create MongoDB client - check MONGO_URI in .env", exc_info=True)
    raise

# Collections
users_collection = db["users"]
articles_collection = db["articles"]
interactions_collection = db["interactions"]