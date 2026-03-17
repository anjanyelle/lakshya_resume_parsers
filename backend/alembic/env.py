import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, pool

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from app.core.config import get_settings  # noqa: E402
from app.models import Base  # noqa: E402
from app.models.additional_models import Project, Publication, Volunteer, Award, Reference, AdditionalText  # noqa: E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
database_url = str(settings.DATABASE_URL).replace("%", "%%")
config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata

# Migrations are written for PostgreSQL (UUID, JSONB, ENUM). Require it.
if database_url and "sqlite" in database_url.lower():
    raise SystemExit(
        "Alembic migrations require PostgreSQL. DATABASE_URL is set to SQLite. "
        "Set DATABASE_URL to a postgresql+psycopg2://... URL (e.g. in backend/.env)."
    )


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Use the same DATABASE_URL as the app (from .env / get_settings())."""
    connectable = create_engine(
        str(settings.DATABASE_URL),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
