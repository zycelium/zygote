"""
Example agent.
"""
from zycelium.zygote.agent import Agent

agent = Agent(name="hello", debug=True)


@agent.on_startup()
@agent.on_interval(minutes=1)
async def example():
    """Example function."""
    await agent.emit("hello", {"message": "Hello, world!"})
