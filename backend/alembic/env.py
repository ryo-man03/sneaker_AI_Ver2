# file: alembic/env.py
from importlib import import_module
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

settings = import_module("app.core.settings").settings
Base = import_module("app.db.base").Base
import_module("app.models.market")
import_module("app.models.sneaker")
import_module("app.models.stock")
import_module("app.models.wishlist")
import_module("app.models.closet")
import_module("app.models.price_alert")
import_module("app.models.notification_event")

config = context.config
sync_url = settings.database_url.replace("+aiosqlite", "")
config.set_main_option("sqlalchemy.url", sync_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
