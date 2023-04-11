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

    async def create_space(
        self, name: str, data: Optional[dict] = None, meta: Optional[dict] = None
    ) -> dict:
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

    async def get_space(self, space_uuid: int) -> dict:
        """Get space."""
        self.logger.info("Getting space")
        try:
            space_obj = await Space.get(uuid=space_uuid)
            return (await PydanticSpace.from_tortoise_orm(space_obj)).dict()
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get space: %s", space_uuid)
            return {"success": False}

    async def get_spaces(self) -> dict:
        """Get spaces."""
        self.logger.info("Getting spaces")
        try:
            spaces = await PydanticSpaceList.from_queryset(Space.all())
            return {"spaces": spaces.dict()["__root__"]}
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get spaces")
            return {"success": False}

    async def update_space(
        self,
        space_uuid: int,
        name: str,
        data: Optional[dict] = None,
        meta: Optional[dict] = None,
    ) -> dict:
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

    async def delete_space(self, space_uuid: int) -> dict:
        """Delete space."""
        self.logger.info("Deleting space")
        try:
            space_obj = await Space.get(id=space_uuid)
            await space_obj.delete()
            return {"success": True}
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to delete space: %s", space_uuid)
            return {"success": False}

    async def create_agent(
        self, name: str, data: Optional[dict] = None, meta: Optional[dict] = None
    ) -> dict:
        """Create agent."""
        self.logger.info("Creating agent")
        data = data or {}
        meta = meta or {}
        try:
            agent_obj = await Agent.create(name=name, data=data, meta=meta)
            return (await PydanticAgent.from_tortoise_orm(agent_obj)).dict()
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to create agent: %s", name)
            return {"success": False}

    async def get_agent(self, agent_uuid: int) -> dict:
        """Get agent."""
        self.logger.info("Getting agent")
        try:
            agent_obj = await Agent.get(uuid=agent_uuid)
            return (await PydanticAgent.from_tortoise_orm(agent_obj)).dict()
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get agent: %s", agent_uuid)
            return {"success": False}
    
    async def get_agents(self) -> dict:
        """Get agents."""
        self.logger.info("Getting agents")
        try:
            agents = await PydanticAgentList.from_queryset(Agent.all())
            return {"agents": agents.dict()["__root__"]}
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get agents")
            return {"success": False}

    async def update_agent(
        self,
        agent_uuid: int,
        name: str,
        data: Optional[dict] = None,
        meta: Optional[dict] = None,
    ) -> dict:
        """Update agent."""
        self.logger.info("Updating agent")
        data = data or {}
        meta = meta or {}
        try:
            agent_obj = await Agent.get(uuid=agent_uuid)
            agent_obj.name = name  # type: ignore
            agent_obj.data = data  # type: ignore
            agent_obj.meta = meta  # type: ignore
            await agent_obj.save()
            return (await PydanticAgent.from_tortoise_orm(agent_obj)).dict()
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to update agent: %s", agent_uuid)
            return {"success": False}

    async def delete_agent(self, agent_uuid: int) -> dict:
        """Delete agent."""
        self.logger.info("Deleting agent")
        try:
            agent_obj = await Agent.get(uuid=agent_uuid)
            await agent_obj.delete()
            return {"success": True}
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to delete agent: %s", agent_uuid)
            return {"success": False}
