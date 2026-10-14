"""Alembic runs this file for every migration command.

Rails comparison:
  bin/rails db:migrate            ->  uv run alembic upgrade head
  bin/rails db:rollback           ->  uv run alembic downgrade -1
  bin/rails g migration AddFoo    ->  uv run alembic revision --autogenerate -m "add foo"

`--autogenerate` compares the models in app/models with the real database and
writes the migration for you. Always read what it generated before running it.
"""

from logging.config import fileConfig

from sqlalchemy import create_engine, pool

import app.models  # noqa: F401  (registers every model on Base.metadata)
from alembic import context
from app.config import get_settings
from app.db import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
database_url = get_settings().database_url


def run_migrations_offline() -> None:
    """Print the SQL instead of running it: `uv run alembic upgrade head --sql`."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(database_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
