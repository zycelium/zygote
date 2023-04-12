"""
Hello world example.
"""
from zycelium.zygote.agent import Agent


agent = Agent("example")


@agent.on("connect")  # type: ignore
async def connect():
    """On connect."""
    print("Connected")
    await agent.emit("hello", {"name": agent.name})


@agent.on_event("hello")
async def hello(data: dict):
    """On hello."""
    print(f'Hello {data["name"]}')
    await agent.emit("goodbye", {"name": agent.name})


@agent.on_event("goodbye")
async def goodbye(data: dict):
    """On goodbye."""
    print(f'Goodbye {data["name"]}')
    await agent.disconnect()

@agent.on("*")  # type: ignore
async def message(event: str, data: dict):
    """On frame."""
    print(f"Frame: {event} {data}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(
        agent.run(
            "https://localhost:3965/",
            auth={"token": ""},
        )
    )
