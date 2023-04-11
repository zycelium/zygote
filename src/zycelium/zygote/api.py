"""
Zygote API.
"""
from typing import Optional

from tortoise import Tortoise
from tortoise.query_utils import Prefetch

from zycelium.zygote.logging import get_logger
from zycelium.zygote.models import (
    init_db,
    Frame,
    Space,
    Agent,
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
            space_dict = {
                "uuid": space_obj.uuid,
                "name": space_obj.name,
                "data": space_obj.data,
                "meta": space_obj.meta,
            }
            return space_dict
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to create space: %s", name)
            return {"success": False}

    async def get_space(self, space_uuid: int) -> dict:
        """Get space."""
        self.logger.info("Getting space")
        try:
            space_obj = await Space.get(uuid=space_uuid)
            space_dict = {
                "uuid": space_obj.uuid,
                "name": space_obj.name,
                "data": space_obj.data,
                "meta": space_obj.meta,
            }
            return space_dict
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get space: %s", space_uuid)
            return {"success": False}

    async def get_spaces(self) -> dict:
        """Get spaces."""
        self.logger.info("Getting spaces")
        try:
            spaces = await Space.all()
            spaces_list = []
            for space in spaces:
                space_dict = {
                    "uuid": space.uuid,
                    "name": space.name,
                    "data": space.data,
                    "meta": space.meta,
                }
                spaces_list.append(space_dict)
            return {"spaces": spaces_list}
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
            space_dict = {
                "uuid": space_obj.uuid,
                "name": space_obj.name,
                "data": space_obj.data,
                "meta": space_obj.meta,
            }
            return space_dict
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
            agent_dict = {
                "uuid": agent_obj.uuid,
                "name": agent_obj.name,
                "data": agent_obj.data,
                "meta": agent_obj.meta,
            }
            return agent_dict
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to create agent: %s", name)
            return {"success": False}

    async def get_agent(self, agent_uuid: int) -> dict:
        """Get agent."""
        self.logger.info("Getting agent")
        try:
            agent_obj = await Agent.get(uuid=agent_uuid).prefetch_related(
                "spaces", Prefetch("spaces", queryset=Space.all())
            )
            agent_dict = {
                "uuid": agent_obj.uuid,
                "name": agent_obj.name,
                "data": agent_obj.data,
                "meta": agent_obj.meta,
                "spaces": [space.uuid for space in await agent_obj.spaces],
            }
            return agent_dict
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get agent: %s", agent_uuid)
            return {"success": False}

    async def get_agents(self) -> dict:
        """Get agents."""
        self.logger.info("Getting agents")
        try:
            agents = await Agent.all()
            agents_list = []
            for agent in agents:
                agent_dict = {
                    "uuid": agent.uuid,
                    "name": agent.name,
                    "data": agent.data,
                    "meta": agent.meta,
                }
                agents_list.append(agent_dict)
            return {"agents": agents_list}
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
            agent_dict = {
                "uuid": agent_obj.uuid,
                "name": agent_obj.name,
                "data": agent_obj.data,
                "meta": agent_obj.meta,
            }
            return agent_dict
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

    async def join_space(self, space_uuid: int, agent_uuid: int) -> dict:
        """Join space."""
        self.logger.info("Joining space")
        try:
            space_obj = await Space.get(uuid=space_uuid)
            agent_obj = await Agent.get(uuid=agent_uuid)
            await space_obj.agents.add(agent_obj)  # type: ignore
            return {"success": True}
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to join space: %s", space_uuid)
            return {"success": False}

    async def leave_space(self, space_uuid: int, agent_uuid: int) -> dict:
        """Leave space."""
        self.logger.info("Leaving space")
        try:
            space_obj = await Space.get(uuid=space_uuid)
            agent_obj = await Agent.get(uuid=agent_uuid)
            await space_obj.agents.remove(agent_obj)  # type: ignore
            return {"success": True}
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to leave space: %s", space_uuid)
            return {"success": False}

    async def get_joined_spaces(self, agent_uuid: int) -> dict:
        """Get joined spaces."""
        self.logger.info("Getting joined spaces")
        try:
            agent_obj = await Agent.get(uuid=agent_uuid).prefetch_related(
                "spaces", Prefetch("spaces", queryset=Space.all())
            )
            spaces_list = []
            for space in await agent_obj.spaces:
                space_dict = {
                    "uuid": space.uuid,
                    "name": space.name,
                    "data": space.data,
                    "meta": space.meta,
                }
                spaces_list.append(space_dict)
            return {"spaces": spaces_list}
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get joined spaces")
            return {"success": False}

    async def get_unjoined_spaces(self, agent_uuid: int) -> dict:
        """Get unjoined spaces."""
        self.logger.info("Getting unjoined spaces")
        try:
            agent_obj = await Agent.get(uuid=agent_uuid)
            spaces = await Space.all()
            spaces_list = []
            joined_spaces = await agent_obj.spaces
            for space in spaces:
                if space not in joined_spaces:
                    space_dict = {
                        "uuid": space.uuid,
                        "name": space.name,
                        "data": space.data,
                        "meta": space.meta,
                    }
                    spaces_list.append(space_dict)
            return {"spaces": spaces_list}
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get unjoined spaces")
            return {"success": False}

    async def get_joined_agents(self, space_uuid: int) -> dict:
        """Get joined agents."""
        self.logger.info("Getting joined agents")
        try:
            space_obj = await Space.get(uuid=space_uuid).prefetch_related(
                "agents", Prefetch("agents", queryset=Agent.all())
            )
            agents_list = []
            for agent in await space_obj.agents:  # type: ignore
                agent_dict = {
                    "uuid": agent.uuid,
                    "name": agent.name,
                    "data": agent.data,
                    "meta": agent.meta,
                }
                agents_list.append(agent_dict)
            return {"agents": agents_list}
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get joined agents")
            return {"success": False}

    async def get_unjoined_agents(self, space_uuid: int) -> dict:
        """Get unjoined agents."""
        self.logger.info("Getting unjoined agents")
        try:
            space_obj = await Space.get(uuid=space_uuid)
            agents = await Agent.all()
            agents_list = []
            joined_agents = await space_obj.agents  # type: ignore
            for agent in agents:
                if agent not in joined_agents:
                    agent_dict = {
                        "uuid": agent.uuid,
                        "name": agent.name,
                        "data": agent.data,
                        "meta": agent.meta,
                    }
                    agents_list.append(agent_dict)
            return {"agents": agents_list}
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get unjoined agents")
            return {"success": False}

    async def create_frame(
        self,
        kind: str,
        name: str,
        data: Optional[dict] = None,
        meta: Optional[dict] = None,
        agent_uuid: Optional[str] = None,
        space_uuids: Optional[list] = None,
    ):
        """Create frame."""
        self.logger.info("Creating frame")
        if not agent_uuid or not space_uuids:
            raise ValueError("agent_uuid and space_uuids are required")
        data = data or {}
        meta = meta or {}
        space_uuids = space_uuids or []
        try:
            frame_obj = await Frame.create(kind=kind, name=name, data=data, meta=meta)
            if agent_uuid:
                agent_obj = await Agent.get(uuid=agent_uuid)
                frame_obj.agent = agent_obj  # type: ignore
                await frame_obj.save()
            for space_uuid in space_uuids:
                space_obj = await Space.get(uuid=space_uuid)
                await frame_obj.spaces.add(space_obj)  # type: ignore
            frame_dict = {
                "uuid": frame_obj.uuid,
                "kind": frame_obj.kind,
                "name": frame_obj.name,
                "data": frame_obj.data,
                "meta": frame_obj.meta,
            }
            return frame_dict
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to create frame")
            return {"success": False}

    async def get_frame(self, frame_uuid: int) -> dict:
        """Get frame."""
        self.logger.info("Getting frame")
        try:
            frame_obj = await Frame.get(uuid=frame_uuid).prefetch_related(
                "agent",
                Prefetch("agent", queryset=Agent.all()),
                "spaces",
                Prefetch("spaces", queryset=Space.all()),
            )
            spaces_list = [
                {
                    "uuid": space.uuid,
                    "name": space.name,
                    "data": space.data,
                    "meta": space.meta,
                }
                for space in await frame_obj.spaces  # type: ignore
            ]  # type: ignore
            frame_dict = {
                "uuid": frame_obj.uuid,
                "kind": frame_obj.kind,
                "name": frame_obj.name,
                "data": frame_obj.data,
                "meta": frame_obj.meta,
                "agent": {
                    "uuid": frame_obj.agent.uuid,
                    "name": frame_obj.agent.name,
                    "data": frame_obj.agent.data,
                    "meta": frame_obj.agent.meta,
                },
                "spaces": spaces_list,
            }
            return frame_dict
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get frame")
            return {"success": False}

    async def get_frames_for_agent(self, agent_uuid: int) -> dict:
        """Get frames."""
        self.logger.info("Getting frames")
        try:
            agent_obj = await Agent.get(uuid=agent_uuid).prefetch_related(
                "frames", Prefetch("frames", queryset=Frame.all())
            )
            frames_list = []
            for frame in await agent_obj.frames:  # type: ignore
                frame_dict = {
                    "uuid": frame.uuid,
                    "kind": frame.kind,
                    "name": frame.name,
                    "data": frame.data,
                    "meta": frame.meta,
                }
                frames_list.append(frame_dict)
            return {"frames": frames_list}
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get frames")
            return {"success": False}

    async def get_frames_for_space(self, space_uuid: int) -> dict:
        """Get frames."""
        self.logger.info("Getting frames")
        try:
            space_obj = await Space.get(uuid=space_uuid).prefetch_related(
                "frames", Prefetch("frames", queryset=Frame.all())
            )
            frames_list = []
            for frame in await space_obj.frames:  # type: ignore
                frame_dict = {
                    "uuid": frame.uuid,
                    "kind": frame.kind,
                    "name": frame.name,
                    "data": frame.data,
                    "meta": frame.meta,
                }
                frames_list.append(frame_dict)
            return {"frames": frames_list}
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to get frames")
            return {"success": False}

    async def delete_frame(self, frame_uuid: int) -> dict:
        """Delete frame."""
        self.logger.info("Deleting frame")
        try:
            frame_obj = await Frame.get(uuid=frame_uuid)
            await frame_obj.delete()
            return {"success": True}
        except Exception:  # pylint: disable=broad-except
            self.logger.error("Failed to delete frame")
            return {"success": False}
