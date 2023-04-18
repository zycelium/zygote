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


class Instance(Model):
    """Instance model."""

    uuid = fields.UUIDField(pk=True, index=True)
    name = fields.CharField(max_length=128, index=True)
    description = fields.TextField(null=True)
    base_url = fields.CharField(max_length=512, null=True)
    verify_tls_cert = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    me = fields.BooleanField(default=False)

    class Meta:
        """Meta."""

        table = "instance"

    def __str__(self):
        """String representation."""
        return f"Instance {self.name}"

    @classmethod
    async def create_me(
        cls,
        name: str,
        description: Optional[str] = None,
        base_url: Optional[str] = None,
        verify_tls_cert: bool = True,
    ):
        """Create me."""
        instance = await cls.create(
            name=name,
            description=description,
            base_url=base_url,
            verify_tls_cert=verify_tls_cert,
            me=True,
        )
        return instance

    @classmethod
    async def get_me(cls):
        """Get me."""
        instance = await cls.get(me=True)
        return instance

    @classmethod
    async def create_peer(
        cls,
        uuid: str,
        name: str,
        description: Optional[str] = None,
        base_url: Optional[str] = None,
        verify_tls_cert: bool = True,
    ):
        """Create peer."""
        instance = await cls.create(
            uuid=uuid,
            name=name,
            description=description,
            base_url=base_url,
            verify_tls_cert=verify_tls_cert,
        )
        return instance

    @classmethod
    async def get_peer_by_uuid(cls, uuid: str):
        """Get peer by UUID."""
        instance = await cls.get(uuid=uuid)
        return instance

    @classmethod
    async def get_peer_by_name(cls, name: str):
        """Get peer by name."""
        instance = await cls.get(name=name)
        return instance

    @classmethod
    async def get_peers(cls):
        """Get peers."""
        instances = await cls.filter(me=False).all()
        return instances
