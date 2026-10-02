import os
import sys
from logging.config import fileConfig

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import create_engine, pool

from alembic import context
from backend.app.core.config import get_settings
from backend.app.models.base import Base
import backend.app.models  # Ensure all models are loaded

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()

# Use direct connection URL for migrations if available, else standard database_url
env_target_url = os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DB_DIRECT_URL") or settings.database_url
target_url = env_target_url

# Escape % for configparser to avoid ValueError: invalid interpolation syntax
safe_url_for_config = target_url.replace("%", "%%")
config.set_main_option("sqlalchemy.url", safe_url_for_config)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=target_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connect_args = (
        {"check_same_thread": False}
        if target_url.startswith("sqlite")
        else {}
    )

    connectable = create_engine(
        target_url,
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
