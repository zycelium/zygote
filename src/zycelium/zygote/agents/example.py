"""
Example agent.
"""
from zycelium.zygote.agent import Agent

agent = Agent(name="example", debug=True)


@agent.on_startup(delay=1)
@agent.on_interval(minutes=1)
async def example():
    """Example function."""
    await agent.emit("example", {"message": "Hello, world!"})
