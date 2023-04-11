"""
Zygote API.
"""
from typing import Optional

from tortoise import Tortoise

from zycelium.zygote.logging import get_logger
from zycelium.zygote.models import (
    init_db,
    Frame,
    PydanticFrame,
    PydanticFrameIn,
    PydanticFrameList,
    Space,
    PydanticSpace,
    PydanticSpaceIn,
    PydanticSpaceList,
    Agent,
    PydanticAgent,
    PydanticAgentIn,
    PydanticAgentList,
)

class ZygoteAPI:
    """Zygote API."""
    def __init__(self):
        """Initialize."""
        self.logger = get_logger("zygote.api")
        self.logger.info("Initializing Zygote API")

    async def start(self, db_url: str):
        """Initialize database."""
        self.logger.info("Initializing database")
        await init_db(db_url)

    async def stop(self):
        """Stop."""
        self.logger.info("Stopping")
        await Tortoise.close_connections()

    async def create_space(self, name: str, data: Optional[dict] = None, meta: Optional[dict] = None):
        """Create space."""
        self.logger.info("Creating space")
        data = data or {}
        meta = meta or {}
        try:
            space_obj = await Space.create(name=name, data=data, meta=meta)
            return (await PydanticSpace.from_tortoise_orm(space_obj)).dict()
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to create space: %s", name)
            return {"success": False}
    
    async def get_space(self, space_uuid: int):
        """Get space."""
        self.logger.info("Getting space")
        try:
            space_obj = await Space.get(uuid=space_uuid)
            return (await PydanticSpace.from_tortoise_orm(space_obj)).dict()
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get space: %s", space_uuid)
            return {"success": False}
    
    async def get_spaces(self):
        """Get spaces."""
        self.logger.info("Getting spaces")
        try:
            spaces = await PydanticSpaceList.from_queryset(Space.all())
            return spaces.dict()["__root__"]
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get spaces")
            return {"success": False}

    
    async def update_space(self, space_uuid: int, name: str, data: Optional[dict] = None, meta: Optional[dict] = None):
        """Update space."""
        self.logger.info("Updating space")
        data = data or {}
        meta = meta or {}
        try:
            space_obj = await Space.get(uuid=space_uuid)
            space_obj.name = name  # type: ignore
            space_obj.data = data  # type: ignore
            space_obj.meta = meta  # type: ignore
            await space_obj.save()
            return (await PydanticSpace.from_tortoise_orm(space_obj)).dict()
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to update space: %s", space_uuid)
            return {"success": False}
    
    async def delete_space(self, space_uuid: int):
        """Delete space."""
        self.logger.info("Deleting space")
        try:
            space_obj = await Space.get(id=space_uuid)
            await space_obj.delete()
            return {"success": True}
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to delete space: %s", space_uuid)
            return {"success": False}
