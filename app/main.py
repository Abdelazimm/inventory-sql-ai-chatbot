import time
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.config import settings
from app.database.connection import engine, Base
from app.api.routes import auth, chat, sessions, ingest, mutations

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("inventory_sql_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Inventory SQL Chatbot Application...")
    # Initialize database tables on startup
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}")
    yield
    logger.info("Shutting down Inventory SQL Chatbot Application...")


app = FastAPI(
    title="Inventory SQL AI Chatbot API",
    description="Production-grade AI Analytics Assistant for Relational Inventory Databases",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-MS"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {response.status_code} ({process_time}ms)")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."}
    )


# Health and Readiness endpoints
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "service": "inventory-sql-ai-chatbot", "version": "1.0.0"}


@app.get("/ready", tags=["System"])
def readiness_check():
    # Verify DB connectivity
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    return {
        "status": "ready" if db_status == "connected" else "degraded",
        "database": db_status,
        "llm_configured": bool(settings.OPENAI_API_KEY)
    }


# Include Routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(ingest.router)
app.include_router(mutations.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
