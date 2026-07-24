from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.models import Base

# Import models so Alembic discovers their tables.
import app.models  # noqa: F401


# Alembic configuration object.
config = context.config


# Configure logging from alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy metadata containing all imported models.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Generate SQL migration commands without opening
    a live database connection.
    """

    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Connect to PostgreSQL and run migrations.
    """

    connectable = create_engine(
        settings.database_url,
        poolclass=NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()