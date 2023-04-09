"""
Zygote agent.
"""
import asyncio
import logging
from typing import Optional

import socketio
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Agent:
    """Zygote agent."""

    def __init__(self, name: str, debug: bool = False) -> None:
        self.name = name
        self.debug = debug
        self.config = {}
        self._log = None  # type: logging.Logger  # type: ignore
        self._sio = self._init_sio()
        self._scheduler = self._init_scheduler()
        self._on_startup_handler = None

    def _init_sio(self) -> socketio.AsyncClient:
        sio = socketio.AsyncClient(ssl_verify=False)
        return sio

    def _init_log(self, name: str, debug: bool) -> logging.Logger:
        log = logging.getLogger(name)
        log.setLevel(logging.DEBUG if debug else logging.INFO)
        log.propagate = False
        formatter = logging.Formatter(
            "%(asctime)s - %(filename)s:%(lineno)s  - %(name)s - %(levelname)s - %(message)s"
        )
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG if debug else logging.INFO)
        handler.setFormatter(formatter)
        log.addHandler(handler)
        return log

    def _init_scheduler(self) -> AsyncIOScheduler:
        scheduler = AsyncIOScheduler()
        return scheduler

    def _start_scheduler(self) -> None:
        self._scheduler.start()

    def _stop_scheduler(self) -> None:
        self._scheduler.shutdown()

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

    async def start(self, url: str, debug: bool = False, delay: float = 1, auth: Optional[dict] = None) -> None:
        """Start the agent."""
        self._log = self._init_log(name=self.name, debug=debug)
        await asyncio.sleep(delay)
        self._log.info("Starting agent...")
        await self._sio.connect(url, auth=auth)
        await self._init_config()
        self._log.info("Agent started.")
        self._start_scheduler()
        if self._on_startup_handler:
            await self._on_startup_handler()  # type: ignore
        while True:
            await asyncio.sleep(1)

    async def stop(self) -> None:
        """Stop the agent."""
        assert self._log is not None
        self._log.info("Stopping agent...")
        self._stop_scheduler()
        await self._sio.disconnect()
        self._log.info("Agent stopped.")

    async def emit(self, name: str, data: dict) -> None:
        """Emit event."""
        frame = {"kind": "event", "name": name, "data": data}
        await self._sio.emit("event", data=frame)

    def on(self, name: str):  # pylint: disable=invalid-name
        """Frame handler."""

        def decorator(func):
            self._sio.on(name, func)
            return func

        return decorator

    def on_event(self, name: str):
        """Event handler."""

        def decorator(func):
            async def wrapper(kind, frame):
                if kind == "event" and frame["name"] == name:
                    await func(frame)

            self._sio.on(name, wrapper)
            return func

        return decorator

    async def _init_config(self) -> None:
        """Initialize config."""
        frame = await self._sio.call("command", {"kind": "command", "name": "config", "data": self.config}, namespace="/", timeout=10)
        self.config = frame["data"]
        self._log.info("Config initialized: %s", self.config)
