"""
Database models.
"""
from tortoise.models import Model
from tortoise import Tortoise, fields

from zycelium.zygote.signals import database_init



class Frame(Model):
    """Frame model"""

    uuid = fields.UUIDField(pk=True)
    kind = fields.CharField(max_length=16)
    name = fields.CharField(max_length=64)
    data = fields.JSONField()
    space = fields.ForeignKeyField("models.Space", related_name="frames")
    sender = fields.ForeignKeyField("models.Agent", related_name="frames")
    timestamp = fields.DatetimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.kind}({self.name})"


class Space(Model):
    """Space model"""

    uuid = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=64, unique=True)
    description = fields.TextField(null=True)
    created = fields.DatetimeField(auto_now_add=True)
    updated = fields.DatetimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name}"


class Agent(Model):
    """Agent model"""

    uuid = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=64, unique=True)
    description = fields.TextField(null=True)
    created = fields.DatetimeField(auto_now_add=True)
    updated = fields.DatetimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name}"


class AgentSpace(Model):
    """AgentSpace model"""

    agent = fields.ForeignKeyField("models.Agent", related_name="spaces")
    space = fields.ForeignKeyField("models.Space", related_name="agents")

    class Meta:
        """Meta class"""

        unique_together = ("agent", "space")

    def __str__(self) -> str:
        return f"{self.agent} in {self.space}"


async def init_db(db_url: str):
    """Initialize database"""

    Tortoise.init_models(["zycelium.zygote.models"], "models")
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["zycelium.zygote.models"]},
    )
    await Tortoise.generate_schemas()
    await database_init.send(f"db_init: {db_url}")

