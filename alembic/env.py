import asyncio
from logging.config import fileConfig
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from alembic import context
from settings import settings
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


from lib.models import Base
from users.models import *  # noqa
from messages.models import * # noqa
from llms.models import * # noqa

target_metadata = Base.metadata


def _strip_url_query_keys(url: str, keys: list[str]) -> str:
    parsed = urlparse(url)
    qs = dict(parse_qsl(parsed.query, keep_blank_values=True))
    for k in keys:
        qs.pop(k, None)
    new_query = urlencode(qs)
    new_parsed = parsed._replace(query=new_query)
    return urlunparse(new_parsed)


def run_migrations_offline() -> None:
    url = settings.get_db_str()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = settings.get_db_str()
    connect_args = settings.build_connect_args()
    clean_url = _strip_url_query_keys(url, ["sslmode"]) if "sslmode" in url else url
    async_connectable = create_async_engine(clean_url, poolclass=pool.NullPool, connect_args=connect_args)

    async def do_run_async_migrations() -> None:
        async with async_connectable.connect() as connection:
            await connection.run_sync(
                lambda sync_conn: context.configure(connection=sync_conn, target_metadata=target_metadata)
            )

            async with connection.begin():
                await connection.run_sync(lambda sync_conn: context.run_migrations())

    try:
        asyncio.run(do_run_async_migrations())
    finally:
        async_connectable.sync_engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
