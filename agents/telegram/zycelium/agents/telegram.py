"""
Telegram agent
"""
from pathlib import Path
from traceback import format_exc
from pyrogram.client import Client as TelegramClient
from pyrogram.handlers.message_handler import MessageHandler
from zycelium.zygote.agent import Agent, config

# pyright: reportOptionalMemberAccess=false


@config
class Config:
    """Config."""

    api_id: str = ""
    api_hash: str = ""
    bot_name: str = ""
    bot_token: str = ""
    chat_id: int = 0


agent = Agent(name="telegram")
TG = None

agent.config = Config()


async def validate_config():
    """Validate config."""
    if not agent.config.api_id:
        await agent.emit("telegram/error", {"message": "Telegram API ID not provided."})
        return False
    if not agent.config.api_hash:
        await agent.emit(
            "telegram/error", {"message": "Telegram API Hash not provided."}
        )
        return False
    if not agent.config.bot_name:
        await agent.emit(
            "telegram/error", {"message": "Telegram Bot Name not provided."}
        )
        return False
    if not agent.config.bot_token:
        await agent.emit(
            "telegram/error", {"message": "Telegram Bot Token not provided."}
        )
        return False
    if not agent.config.chat_id:
        await agent.emit(
            "telegram/error", {"message": "Telegram Chat ID not provided."}
        )
        return False
    return True


async def message_handler(_client, message):
    """Handle incoming messages."""
    await agent.emit("telegram/message", {"message": message.text})


@agent.on_startup(delay=1)
async def startup():
    """Start Telegram bot."""
    if not await validate_config():
        return
    await agent.emit("telegram/start", {"message": "Starting Telegram bot."})
    global TG  # pylint: disable=global-statement
    try:
        if Path(f"{agent.config.bot_name}.session").exists():
            TG = TelegramClient(name=agent.config.bot_name)
        else:
            TG = TelegramClient(
                name=agent.config.bot_name,
                api_id=agent.config.api_id,
                api_hash=agent.config.api_hash,
                bot_token=agent.config.bot_token,
            )
        TG.add_handler(MessageHandler(message_handler))
        await TG.start()
        await agent.emit("telegram/started", {"message": "Telegram bot started."})
        await TG.send_message(int(agent.config.chat_id), "Telegram bot started.")
    except Exception:  # pylint: disable=broad-except
        await agent.emit("telegram/error", {"message": format_exc()})


@agent.on_shutdown()
async def shutdown():
    """Shutdown Telegram bot."""
    if TG:
        await TG.stop()


@agent.on_event("telegram/send")
async def send(frame):
    """Send message."""
    if not await validate_config():
        return
    if not TG:
        await agent.emit("telegram/error", {"message": "Telegram bot not started."})
        return
    if not frame["data"]["message"]:
        await agent.emit("telegram/error", {"message": "No message provided."})
        return
    try:
        await TG.send_message(agent.config.chat_id, frame["data"]["message"])
        await agent.emit("telegram/info", {"message": "Message sent."})
    except Exception:  # pylint: disable=broad-except
        await agent.emit("telegram/error", {"message": format_exc()})


if __name__ == "__main__":
    import asyncio

    asyncio.run(
        agent.run(
            "https://localhost:3965/",
            auth={"token": ""},
        )
    )
