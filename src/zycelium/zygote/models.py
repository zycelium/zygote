"""
Zygote Models.
"""
from typing import Optional

from tortoise import Tortoise, fields
from tortoise.models import Model

from zycelium.zygote.signals import database_started, database_stopped


async def start_database(db_url: str):
    """Start database."""
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["zycelium.zygote.models"]},
    )
    await Tortoise.generate_schemas()
    await database_started.send(db_url)


async def stop_database():
    """Stop database."""
    await Tortoise.close_connections()
    await database_stopped.send("")

