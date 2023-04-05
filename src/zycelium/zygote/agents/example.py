"""
Example agent.
"""
from zycelium.zygote.agent import Agent

agent = Agent(name="example", debug=True)


@agent.on_interval(seconds=5)
async def example():
    """Example function."""
    await agent.emit(event="example", data={"message": "Hello, world!"})
