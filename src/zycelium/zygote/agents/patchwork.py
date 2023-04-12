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
