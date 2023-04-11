"""
Database models.
"""
from tortoise import Tortoise, fields
from tortoise.models import Model

from zycelium.zygote.signals import database_init


async def init_db(db_url: str):
    """Initialize database"""

    Tortoise.init_models(["zycelium.zygote.models"], "models")
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["zycelium.zygote.models"]},
    )
    await Tortoise.generate_schemas()
    await database_init.send(f"db_init: {db_url}")


class Frame(Model):
    """Frame model"""

    uuid = fields.UUIDField(pk=True, index=True)
    kind = fields.CharField(max_length=16, index=True, default="event")
    name = fields.CharField(max_length=64, index=True, null=False)
    data = fields.JSONField(default={})
    meta = fields.JSONField(default={})
    time = fields.DatetimeField(auto_now_add=True, index=True)
    agent = fields.ForeignKeyField("models.Agent", related_name="frames", null=True)

    def __str__(self) -> str:
        return f"{self.kind}({self.name})"

    class Meta:
        """Meta class"""

        table = "frame"
        ordering = ["-time"]


class Space(Model):
    """Space model"""

    uuid = fields.UUIDField(pk=True, index=True)
    name = fields.CharField(max_length=64, index=True, null=False, unique=True)
    data = fields.JSONField(default={})
    meta = fields.JSONField(default={})
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True, index=True)
    frames = fields.ManyToManyField(
        "models.Frame", related_name="spaces", through="frame_space"
    )

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        """Meta class"""

        table = "space"
        ordering = ["name"]


class Agent(Model):
    """Agent model"""

    uuid = fields.UUIDField(pk=True, index=True)
    name = fields.CharField(max_length=64, index=True, null=False, unique=True)
    data = fields.JSONField(default={})
    meta = fields.JSONField(default={})
    spaces = fields.ManyToManyField(
        "models.Space", related_name="agents", through="agent_space"
    )
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True, index=True)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        """Meta class"""

        table = "agent"
        ordering = ["name"]



class AuthToken(Model):
    """AuthToken model"""

    uuid = fields.UUIDField(pk=True, index=True)
    token = fields.CharField(max_length=64, index=True, null=False, unique=True)
    agent = fields.ForeignKeyField("models.Agent", related_name="tokens", null=True)
    revoked = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True, index=True)

    def __str__(self) -> str:
        return f"{self.token}"

    class Meta:
        """Meta class"""

        table = "auth_token"
        ordering = ["-created_at"]
