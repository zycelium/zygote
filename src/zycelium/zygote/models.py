"""
Database models.
"""
from tortoise import Tortoise, fields
from tortoise.models import Model
from tortoise.contrib.pydantic.creator import (
    pydantic_model_creator,
    pydantic_queryset_creator,
)

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

    def __str__(self) -> str:
        return f"{self.kind}({self.name})"

    class Meta:
        """Meta class"""

        table = "frame"
        ordering = ["-time"]


PydanticFrame = pydantic_model_creator(Frame, name="Frame")
PydanticFrameIn = pydantic_model_creator(
    Frame, name="FrameIn", exclude_readonly=True, exclude=("uuid", "time")
)
PydanticFrameList = pydantic_queryset_creator(Frame, name="FrameList")


class Space(Model):
    """Space model"""

    uuid = fields.UUIDField(pk=True, index=True)
    name = fields.CharField(max_length=64, index=True, null=False)
    data = fields.JSONField(default={})
    meta = fields.JSONField(default={})
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True, index=True)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        """Meta class"""

        table = "space"
        ordering = ["name"]


PydanticSpace = pydantic_model_creator(Space, name="Space")
PydanticSpaceIn = pydantic_model_creator(
    Space,
    name="SpaceIn",
    exclude_readonly=True,
    exclude=("uuid", "created_at", "updated_at"),
)
PydanticSpaceList = pydantic_queryset_creator(Space, name="SpaceList")
