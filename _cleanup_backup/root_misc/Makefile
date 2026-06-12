.PHONY: help build up dev down logs migrate test clean

help:
	@echo "Available commands:"
	@echo "  make build    - Build all containers"
	@echo "  make up       - Start all containers"
	@echo "  make dev      - Start development environment"
	@echo "  make down     - Stop all containers"
	@echo "  make logs     - View logs"
	@echo "  make migrate  - Run database migrations"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Remove containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d

dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	docker-compose exec backend alembic upgrade head

test:
	docker-compose exec backend pytest

clean:
	docker-compose down -v
