"""
Example agent.
"""
from zycelium.zygote.agent import Agent

agent = Agent(name="patchwork")


@agent.on_event("openweather/current")
async def weather(frame):
    """Handle weather event."""
    await agent.emit(
        "telegram/send",
        {"message": f"Current temperature: {frame['data']['main']['temp']}"},
    )


@agent.on_event("fediverse/bookmark")
async def bookmark(frame):
    """Handle bookmark event."""
    await agent.emit(
        "telegram/send",
        {"message": f"New bookmark: {frame['data']['url']}"},
    )
    content = frame["data"]["content"]
    url = frame["data"]["url"]
    await agent.emit(
        "logseq/append-to-journal",
        {
            "text": f"url:: {url}\n{content}",
        },
    )


@agent.on_event("telegram/message")
async def telegram_message(frame):
    """Handle telegram message event."""
    message = frame["data"]["message"]
    await agent.emit(
        "logseq/append-to-journal",
        {
            "text": message,
        },
    )


@agent.on_event("logseq/new-journal-entry")
async def logseq_new_journal_entry(frame):
    """Handle logseq new journal entry event."""
    block_uuid = frame["data"]["block_uuid"]
    await agent.emit(
        "telegram/send",
        {
            "message": f"New journal entry: {block_uuid}",
        },
    )