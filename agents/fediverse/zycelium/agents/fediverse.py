"""
Fetch bookmarks using Mastodon API.
"""
from mastodon import Mastodon
from zycelium.zygote.agent import Agent, config
from zycelium.zygote.logging import get_logger

# pyright: reportOptionalMemberAccess=false

log = get_logger("zygote.agent.fediverse")


@config
class Config:
    """Config."""

    api_base_url: str = ""
    app_name: str = "Zycelium"
    client_key: str = ""
    client_secret: str = ""
    access_token: str = ""
    last_seen_id: int = 0


agent = Agent("fediverse")

agent.config = Config()


async def validate_config():
    """Validate config."""
    if not agent.config.api_base_url:
        log.error("Please set api_base_url in config")
        return False
    if not agent.config.app_name:
        log.error("Please set app_name in config")
        return False
    if not agent.config.client_key:
        log.error("Please set client_key in config")
        return False
    if not agent.config.client_secret:
        log.error("Please set client_secret in config")
        return False
    if not agent.config.access_token:
        log.error("Please set access_token in config")
        return False
    return True


@agent.on_startup(delay=1)
async def startup():
    """Startup."""
    if not await validate_config():
        return


@agent.on_interval(seconds=20)
async def get_bookmarks():
    """Get bookmarks."""
    log.info("Getting bookmarks")
    mastodon = Mastodon(
        client_id=agent.config.client_key,
        client_secret=agent.config.client_secret,
        access_token=agent.config.access_token,
        api_base_url=agent.config.api_base_url,
    )

    bookmarks = mastodon.bookmarks(limit=10)

    for bookmark in bookmarks:
        if bookmark.id != agent.config.last_seen_id:
            await agent.config_update(last_seen_id=bookmark.id)
        else:
            log.info("Stopping, last_seen_id is %s", agent.config.last_seen_id)
            break

        bookmark_dict = {
            "id": bookmark.id,
            "url": bookmark.url,
            "content": bookmark.content,
            "created_at": bookmark.created_at.isoformat(),
            "account": {
                "id": bookmark.account.id,
                "username": bookmark.account.username,
                "acct": bookmark.account.acct,
                "display_name": bookmark.account.display_name,
            },
        }
        if bookmark.media_attachments:
            bookmark_dict["media_attachments"] = [
                {
                    "id": media.id,
                    "type": media.type,
                    "url": media.url,
                    "preview_url": media.preview_url,
                    "description": media.description,
                }
                for media in bookmark.media_attachments
            ]
        if bookmark.card:
            bookmark_dict["card"] = {
                "url": bookmark.card.url,
                "title": bookmark.card.title,
                "description": bookmark.card.description,
                "type": bookmark.card.type,
            }
        await agent.emit("fediverse/bookmark", bookmark_dict)
        log.info("Sent bookmark %s", bookmark_dict["id"])


if __name__ == "__main__":
    import asyncio

    asyncio.run(
        agent.run(
            "https://localhost:3965/",
            auth={"token": ""},
        )
    )
