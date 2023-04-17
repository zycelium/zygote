"""
Log to file agent.
"""
import asyncio
import json

from zycelium.zygote.agent import Agent, config

# pyright: reportOptionalMemberAccess=false


@config
class Config:
    """Log to file agent config."""

    log_file: str = "zygote_frames.log"


agent = Agent(name="log_to_file")

agent.config = Config()


@agent.on("*")  # type: ignore
async def log_to_file(_kind, frame):
    """Log frames to file."""
    try:
        with open(agent.config.log_file, "a", encoding="utf-8") as file:
            file.write(json.dumps(frame) + "\n")
    except asyncio.CancelledError:
        pass