"""
Hello world example.
"""
from zycelium.zygote.agent import Agent


agent = Agent("example")


@agent.on("connect")
async def on_connect() -> None:
    """On connect."""
    await agent.emit("hello", {"name": agent.name})


@agent.on("hello")
async def on_hello(data: dict) -> None:
    """On hello."""
    print(f'Hello {data["name"]}')
    await agent.disconnect()


@agent.on("*")
async def on_frame(event: str, data: dict) -> None:
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
