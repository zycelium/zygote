"""
Hello world example.
"""
from zycelium.zygote.agent import Agent, config


@config
class Config:
    """Config."""

    shout: bool = False


agent = Agent("example")
agent.config = Config()


@agent.on_startup()
async def on_startup():
    """On startup."""
    await agent.emit("hello", {"name": agent.name})


@agent.on_event("hello")
async def hello(frame: dict):
    """On hello."""
    if agent.config.shout:  # type: ignore
        print(f'HELLO {frame["data"]["name"].upper()}')
    else:
        print(f'Hello {frame["data"]["name"]}')


@agent.on_event("goodbye")
async def goodbye(frame: dict):
    """On goodbye."""
    print(f'Goodbye {frame["data"]["name"]}')
    await agent.disconnect()


@agent.on("*")  # type: ignore
async def message(event: str, data: dict):
    """On frame."""
    print(f"Frame: {event} {data}")


@agent.on_interval(seconds=2)
async def on_interval():
    """On interval."""
    await agent.emit("goodbye", {"name": agent.name})


if __name__ == "__main__":
    import asyncio

    asyncio.run(
        agent.run(
            "https://localhost:3965/",
            auth={"token": ""},
        )
    )
