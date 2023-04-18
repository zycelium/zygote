"""
Zygote Models.
"""
from typing import Optional

from tortoise import Tortoise, fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist  # pylint: disable=unused-import

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


class Peer(Model):
    """Peer model."""

    uuid = fields.UUIDField(pk=True, index=True)
    name = fields.CharField(max_length=128, index=True)
    description = fields.TextField(null=True)
    base_url = fields.CharField(max_length=512, null=True)
    verify_tls_cert = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """Meta."""

        table = "peer"

    def __str__(self):
        """String representation."""
        return f"Peer {self.name}"


__all__ = [
    "DoesNotExist",
    "Peer",
    "start_database",
    "stop_database",
]