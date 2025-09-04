import logging
import sys
from datetime import datetime


def setup_logging():
    """Настройка логирования для приложения"""

    # Формат логов
    log_format = "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"

    # Настройка основного логгера
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Настройка логгеров для библиотек
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)

    # Логгер приложения
    logger = logging.getLogger("payment_service")
    logger.setLevel(logging.INFO)

    logger.info("Система логирования инициализирована")
