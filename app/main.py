import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.database import init_db
from .routers import auth, payments
from .utils.logger import setup_logging

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Запуск приложения...")
    await init_db()
    logger.info("База данных инициализирована")
    yield
    # Shutdown
    logger.info("Завершение работы приложения...")


app = FastAPI(
    title="Payment Service API",
    description="Сервис для создания и управления платежами",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "Payment Service API", "version": "1.0.0", "docs": "/docs", "health": "OK"}


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "healthy", "service": "payment-service"}
