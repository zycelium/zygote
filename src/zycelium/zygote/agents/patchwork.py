"""
Example agent.
"""
from zycelium.zygote.agent import Agent

agent = Agent(name="patchwork")


@agent.on_event("openweather/current")
async def weather(frame):
    """Handle weather event."""
    await agent.emit(
        "telegram/send", {"message": f"Current temperature: {frame['data']['main']['temp']}"}
    )


@agent.on_event("fediverse/bookmark")
async def bookmark(frame):
    """Handle bookmark event."""
    await agent.emit(
        "telegram/send",
        {"message": f"New bookmark: {frame['data']['url']}"},
    )