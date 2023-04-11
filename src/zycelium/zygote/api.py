"""
Zygote API.
"""
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
