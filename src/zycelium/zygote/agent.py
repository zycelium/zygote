"""
Agent.
"""
import asyncio
from typing import Awaitable, Callable, Optional

import socketio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from socketio.exceptions import ConnectionError as SioConnectionError
from zycelium.dataconfig import dataconfig as config
from zycelium.zygote.logging import get_logger


class Agent:
    """Agent."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.config = None  # type: Optional[config.Config]
        self.spaces = {}
        self.log = get_logger("zygote.agent")
        self.sio = socketio.AsyncClient(ssl_verify=False)
        self.on = self.sio.on  # pylint: disable=invalid-name
        self.sio.on("command", self._handle_command)
        self._scheduler = self._init_scheduler()
        self._on_startup_handler = None  # type: Optional[Callable[[], Awaitable[None]]]
        self._on_shutdown_handler = (
            None
        )  # type: Optional[Callable[[], Awaitable[None]]]

    def _init_scheduler(self) -> AsyncIOScheduler:
        scheduler = AsyncIOScheduler()
        return scheduler

    def _start_scheduler(self) -> None:
        self._scheduler.start()

    def _stop_scheduler(self) -> None:
        self._scheduler.shutdown()

    async def _handle_command(self, data: dict) -> None:
        """On command."""
        command = data["name"]
        if command == "identity":
            agent_name = data["data"]["name"]
            spaces = data["data"]["spaces"]
            self.name = agent_name
            self.spaces = {space["name"]: space for space in spaces}
            self.log.info(
                "Agent %s joined spaces: %s", agent_name, ", ".join(self.spaces.keys())
            )
        elif command == "config":
            if self.config is None:
                self.log.warning("Agent not configured")
                return
            self.config.from_dict(data["data"])
            self.log.info("Agent configured: %s", data["data"])
        else:
            self.log.warning("Unknown command: %s", command)

    async def _configure(self) -> None:
        """Configure agent."""
        if self.config is None:
            return
        await self.sio.emit(
            "command-config",
            {
                "kind": "command",
                "name": "config",
                "data": self.config.to_dict(),
            },
            namespace="/",
        )

    async def run(self, url: str, auth: dict) -> None:
        """Run agent."""
        try:
            self.log.info("Connecting to %s", url)
            await self.connect(url, auth=auth)
            await self._configure()
        except SioConnectionError:
            self.log.fatal("Connection error: check network connection, url or auth.")
            return

        try:
            if self._on_startup_handler:
                await self._on_startup_handler()
            self._start_scheduler()
            await self.sio.wait()
        except asyncio.exceptions.CancelledError:
            self.log.info("Agent %s stopped.", self.name)
        finally:
            if self._on_shutdown_handler:
                await self._on_shutdown_handler()
            self._stop_scheduler()
            await self.disconnect()

    async def connect(self, url: str, auth: dict) -> None:
        """Connect to server."""
        await self.sio.connect(url, auth=auth)

    async def disconnect(self) -> None:
        """Disconnect from server."""
        await self.sio.disconnect()

    async def emit(self, name: str, data: Optional[dict] = None) -> None:
        """Emit event."""
        kind = "event"
        frame = {
            "kind": kind,
            "name": name,
            "data": data or {},
        }
        await self.sio.emit(f"{kind}-{name}", frame)

    def on_startup(self, delay: float = 0.0):
        """Startup event handler."""

        def wrapper(func):
            async def wrapped(*args, **kwargs):
                await asyncio.sleep(delay)
                await func(*args, **kwargs)

            if asyncio.iscoroutinefunction(func):
                self._on_startup_handler = wrapped
            else:
                raise TypeError("on_startup decorator must be used with a coroutine")
            return func

        return wrapper

    def on_shutdown(self):
        """Shutdown event handler."""

        def wrapper(func):
            if asyncio.iscoroutinefunction(func):
                self._on_shutdown_handler = func
            else:
                raise TypeError("on_shutdown decorator must be used with a coroutine")
            return func

        return wrapper

    def on_event(self, name: str):
        """On event."""

        def wrapper(func) -> None:
            """Connect wrapper."""

            async def inner(frame) -> None:
                """Wrapper."""
                if frame["name"] == name:
                    await func(frame)

            self.sio.on(f"event-{name}", inner)
            return func

        return wrapper

    def on_interval(
        self,
        seconds: Optional[float] = None,
        minutes: Optional[float] = None,
        hours: Optional[float] = None,
        days: Optional[float] = None,
        weeks: Optional[float] = None,
        max_instances: int = 1,
        replace_existing: bool = False,
        id: Optional[str] = None,  # pylint: disable=redefined-builtin,invalid-name
        name: Optional[str] = None,
    ):  # pylint: disable=too-many-arguments
        """Schedule function to be called on interval"""

        def decorator(func):
            interval_kwargs = {
                "seconds": seconds,
                "minutes": minutes,
                "hours": hours,
                "days": days,
                "weeks": weeks,
            }
            interval_kwargs = {k: v for k, v in interval_kwargs.items() if v}
            self._scheduler.add_job(
                func,
                max_instances=max_instances,
                replace_existing=replace_existing,
                trigger="interval",
                id=id,
                name=name,
                **interval_kwargs,
            )
            return func

        return decorator

    def on_cron(
        self,
        year: Optional[str] = None,
        month: Optional[str] = None,
        day: Optional[str] = None,
        week: Optional[str] = None,
        day_of_week: Optional[str] = None,
        hour: Optional[str] = None,
        minute: Optional[str] = None,
        second: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timezone: Optional[str] = None,
        max_instances: int = 1,
        replace_existing: bool = False,
        id: Optional[str] = None,  # pylint: disable=redefined-builtin,invalid-name
        name: Optional[str] = None,
    ):  # pylint: disable=too-many-arguments,too-many-locals
        """Schedule function to be called on cron"""

        def decorator(func):
            self._scheduler.add_job(
                func,
                max_instances=max_instances,
                replace_existing=replace_existing,
                trigger="cron",
                id=id,
                name=name,
                year=year,
                month=month,
                day=day,
                week=week,
                day_of_week=day_of_week,
                hour=hour,
                minute=minute,
                second=second,
                start_date=start_date,
                end_date=end_date,
                timezone=timezone,
            )
            return func

        return decorator
