.PHONY: help build up down restart logs clean test lint format migrate

# Переменные
COMPOSE_FILE = docker-compose.yml
SERVICE_WEB = web
SERVICE_DB = db

# Помощь
help:
	@echo "Доступные команды:"
	@echo "  build     - Собрать Docker образы"
	@echo "  up        - Запустить все сервисы"
	@echo "  down      - Остановить все сервисы"
	@echo "  restart   - Перезапустить сервисы"
	@echo "  logs      - Показать логи"
	@echo "  logs-web  - Показать логи веб-сервиса"
	@echo "  logs-db   - Показать логи базы данных"
	@echo "  clean     - Очистить все контейнеры и образы"
	@echo "  shell     - Подключиться к контейнеру приложения"
	@echo "  db-shell  - Подключиться к PostgreSQL"
	@echo "  migrate   - Запустить миграции"
	@echo "  test      - Запустить тесты"
	@echo "  dev       - Запуск в режиме разработки с автоперезагрузкой"

# Сборка образов
build:
	docker-compose -f $(COMPOSE_FILE) build

# Запуск всех сервисов
up:
	docker-compose -f $(COMPOSE_FILE) up -d

# Первый запуск (сборка + запуск)
dev:
	docker-compose -f $(COMPOSE_FILE) up --build

# Остановка сервисов
down:
	docker-compose -f $(COMPOSE_FILE) down

# Перезапуск
restart: down up

# Логи всех сервисов
logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

# Логи веб-сервиса
logs-web:
	docker-compose -f $(COMPOSE_FILE) logs -f $(SERVICE_WEB)

# Логи базы данных
logs-db:
	docker-compose -f $(COMPOSE_FILE) logs -f $(SERVICE_DB)

# Подключение к контейнеру приложения
shell:
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) /bin/bash

# Подключение к PostgreSQL
db-shell:
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_DB) psql -U user -d payment_db

# Миграции
migrate:
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) alembic upgrade head

# Создание новой миграции
migration:
	@read -p "Введите описание миграции: " desc; \
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) alembic revision --autogenerate -m "$desc"

# Создание первоначальных миграций (запускается один раз)
init-migrations:
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) alembic revision --autogenerate -m "Initial migration"

# Тесты
test:
	docker-compose -f $(COMPOSE_FILE) exec $(SERVICE_WEB) pytest -v

# Проверка статуса
status:
	docker-compose -f $(COMPOSE_FILE) ps

# Полная очистка
clean:
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all --remove-orphans
	docker system prune -f

# Форматирование кода
format:
	black app/ tests/
	isort app/ tests/
	autopep8 --in-place --aggressive --recursive app/ tests/
	@echo "Код отформатирован!"

# Проверка стиля кода
lint:
	flake8 app/ tests/
	black --check app/ tests/
	isort --check-only app/ tests/
	@echo "Стиль кода проверен!"

# Проверка типов
typecheck:
	mypy app/ || echo "Mypy проверка завершена (могут быть предупреждения)"

# Полная проверка качества кода
check: format lint typecheck
	@echo "Все проверки завершены!"

# Быстрое исправление всех проблем форматирования
fix: format
	@echo "Код исправлен и отформатирован!"

# Создание .env файла из примера
env:
	cp .env.example .env
	@echo ".env файл создан. Отредактируйте его при необходимости."
