# alembic/env.py

from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models import Base
from config import settings

config = context.config

config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    """Выполнить миграции в 'offline' режиме.

    В этом режиме мы устанавливаем только URL для конфигурации контекста,
    без создания Engine. Токен SQL будет выводиться непосредственно в файл.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Выполнить миграции в 'online' режиме.

    В этом режиме мы создаем Engine и ассоциируем соединение с контекстом.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Это позволит Alembic отслеживать изменения типов данных
            render_as_batch=True  # Это важно для поддержки ALTER TABLE в SQLite, можно удалить для PostgreSQL
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
