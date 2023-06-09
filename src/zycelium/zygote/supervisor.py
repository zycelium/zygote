"""
Supervisor for processes using multiprocessing.
"""
import asyncio
import multiprocessing
from typing import Callable

from zycelium.zygote.logging import get_logger
from zycelium.zygote.signals import (
    process_started,
    process_stopped,
    supervisor_started,
    supervisor_stopped,
    supervisor_cancelled,
)


class Process:
    """
    Supervised process.
    """

    def __init__(self, name, function, *args, **kwargs):
        self.name = name
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.process = None
        self.log = get_logger(f"zygote.supervisor.process.{self.name}")

    def start(self) -> None:
        """
        Start the agent.
        """
        self.process = multiprocessing.Process(
            target=self.function, args=self.args, kwargs=self.kwargs
        )
        self.process.start()
        self.log.info("Started process %s", self.name)

    def stop(self) -> None:
        """
        Stop the agent.
        """
        if self.process is not None:
            self.process.terminate()
            self.log.info("Terminated process %s", self.name)

    def join(self) -> None:
        """
        Join the agent.
        """
        if self.process is not None:
            self.process.join()

    def is_alive(self) -> bool:
        """
        Check if the agent is alive.
        """
        if self.process is not None:
            return self.process.is_alive()
        return False

    def __enter__(self) -> "Process":
        self.start()
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback) -> None:
        self.stop()
        self.join()


class Supervisor:
    """
    Supervisor for processes.
    """

    def __init__(self):
        self.processes = {}  # type: dict[str, Process]  # type: ignore
        self.log = get_logger("zygote.supervisor")
        self._supervise_loop_task = None

    async def start(self) -> None:
        """
        Start the supervisor.
        """
        self.log.info("Starting supervisor")
        for process in self.processes.values():
            process.start()
            await process_started.send(process.name)

        self._supervise_loop_task = asyncio.get_running_loop().create_task(
            self.supervise_loop()
        )
        await supervisor_started.send("supervisor")
        self.log.info("Started supervisor")

    async def stop(self) -> None:
        """
        Stop the supervisor.
        """
        self.log.info("Stopping supervisor")
        for process in self.processes.values():
            process.stop()
            process.join()
            await process_stopped.send(process.name)

        if self._supervise_loop_task is not None:
            self._supervise_loop_task.cancel()

        await supervisor_stopped.send("supervisor")
        self.log.info("Stopped supervisor")

    async def is_alive(self, name) -> bool:
        """
        Check if process is alive.
        """
        if name not in self.processes:
            return False
        return self.processes[name].is_alive()

    async def add_process(
        self,
        name: str,
        function: Callable,
        *args,
        start: bool = False,
        **kwargs,
    ) -> None:
        """
        Add a process to the supervisor.
        """
        if name in self.processes:
            raise KeyError(f"Process {name} already exists.")
        process = Process(name, function, *args, **kwargs)
        self.processes[name] = process
        if start:
            process.start()
            await process_started.send(name)

    async def remove_process(self, name: str) -> None:
        """
        Remove a process from the supervisor.
        """
        if name in self.processes:
            self.processes[name].stop()
            self.processes[name].join()
            del self.processes[name]
            await process_stopped.send(name)

    async def supervise_loop(self) -> None:
        """
        Supervise all processes.
        """
        while True:
            for process in self.processes.values():
                if not process.is_alive():
                    self.log.error("Process %s died", process.name)
                    await process_stopped.send(process.name)
                    process.start()
                    await process_started.send(process.name)
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                await supervisor_cancelled.send("supervisor")
                break
