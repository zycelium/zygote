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
        self._log = None # self._init_log(name=name, debug=debug)
        self._sio = self._init_sio()
        self._scheduler = self._init_scheduler()

    def _init_sio(self) -> socketio.AsyncClient:
        sio = socketio.AsyncClient()
        return sio

    def _init_log(self, name: str, debug: bool) -> logging.Logger:
        log = logging.getLogger(name)
        log.setLevel(logging.DEBUG if debug else logging.INFO)
        log.propagate = False
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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

    async def start(self, url: str, debug: bool = False, delay: float = 1) -> None:
        """Start the agent."""
        self._log = self._init_log(name=self.name, debug=debug)
        self._log.info("Starting agent...")
        await asyncio.sleep(delay)
        self._start_scheduler()
        await self._sio.connect(url)
        self._log.info("Agent started.")
        while True:
            await asyncio.sleep(1)

    async def stop(self) -> None:
        """Stop the agent."""
        assert self._log is not None
        self._log.info("Stopping agent...")
        self._stop_scheduler()
        await self._sio.disconnect()
        self._log.info("Agent stopped.")

    async def emit(self, event: str, data: dict) -> None:
        """Emit event."""
        await self._sio.emit(event=event, data=data)