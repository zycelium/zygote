"""
Hello world example.
"""
from zycelium.zygote.agent import Agent


agent = Agent("example")


@agent.on("connect")
async def on_connect() -> None:
    """On connect."""
    print("Connected to server")
    await agent.emit("hello", {"name": agent.name})


@agent.on("hello")
async def on_hello(data: dict) -> None:
    """On hello."""
    print(f'Hello {data["name"]}')
    await agent.disconnect()


if __name__ == "__main__":
    import asyncio

    asyncio.run(
        agent.run(
            "https://localhost:3965/",
            auth={"token": ""},
        )
    )
