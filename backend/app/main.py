import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes import auth_routes, article_routes, recommendation_routes
from app.exceptions import AppError
from app.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="NewsPulse AI", version="1.0.0")

# Allow the frontend (served separately as static HTML/CSS/JS) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Logs every request with method, path, status code, and duration."""
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(
        "%s %s -> %s (%sms)",
        request.method, request.url.path, response.status_code, duration_ms,
    )
    return response


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError):
    """Catches all expected application errors and returns a clean, consistent response."""
    logger.warning("AppError on %s %s: %s", request.method, request.url.path, exc.message)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    """Catches anything unhandled so the API never leaks a raw stack trace to the client."""
    logger.error("Unhandled error on %s %s", request.method, request.url.path, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our end. Please try again."},
    )


app.include_router(auth_routes.router)
app.include_router(article_routes.router)
app.include_router(recommendation_routes.router)


@app.on_event("startup")
async def on_startup():
    logger.info("NewsPulse AI backend starting up")


@app.get("/")
async def health_check():
    return {"status": "NewsPulse AI backend is running"}