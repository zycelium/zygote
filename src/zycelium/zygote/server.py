"""
Zygote server agent.
"""
import asyncio
import importlib
import multiprocessing
import pkgutil
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional
from uuid import uuid4

import socketio
import uvicorn
from quart import Quart, render_template
from quart_cors import cors

from zycelium.zygote.agent import Agent


def start_agent(name: str, url: str, debug: bool = False, auth: Optional[dict] = None) -> socketio.AsyncClient:
    """Start agent."""
    agent_module = importlib.import_module(name)
    try:
        print(f"Starting {name} agent...")
        asyncio.run(agent_module.agent.start(url=url, debug=debug, auth=auth))
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass


class Server(Agent):
    """Zygote server agent."""

    def __init__(
        self, name: str, debug: bool = False, *, allow_origin: str = "*"
    ) -> None:
        self.name = name
        self.debug = debug
        self.host = ""
        self.port = 0
        self._allow_origin = allow_origin
        super().__init__(name=name, debug=debug)
        self._base_path = Path(__file__).parent
        self._quart_app = Quart(
            self.name, template_folder=str(self._base_path.joinpath("templates"))
        )
        self._quart_app = cors(self._quart_app, allow_origin=self._allow_origin)
        self._quart_app.config["DEBUG"] = self.debug
        self._sio_app = socketio.ASGIApp(self._sio, self._quart_app)
        self._quart_app.before_serving(self._on_startup)
        self._quart_app.after_serving(self._on_shutdown)
        self._sio.on(event="connect", namespace="/")(self._on_connect)
        self._sio.on(event="disconnect", namespace="/")(self._on_disconnect)
        self._sio.on(event="*", namespace="/")(self._on_event)
        # self._quart_app.template_folder = "templates"
        self._quart_app.route("/")(self._http_index)
        self._agents = {}
        self._agent_processes = {}

    def _init_sio(self) -> socketio.AsyncServer:
        sio = socketio.AsyncServer(
            async_mode="asgi", cors_allowed_origins=self._allow_origin
        )
        return sio

    def _discover_agents(self) -> Iterable[str]:
        """Discover agents."""

        def _iter_namespace(ns_pkg):
            return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

        # Built-in agents
        self._log.info("Discovering built-in agents...")
        namespace = importlib.import_module("zycelium.zygote.agents")
        for _, name, _ in _iter_namespace(namespace):
            self._log.info("Found built-in agent: %s", name)
            yield name

        # Installable agents
        self._log.info("Discovering installed agents")
        namespace = importlib.import_module("zycelium.agents")
        for _, name, _ in _iter_namespace(namespace):
            self._log.info("Found installed agent: %s", name)
            yield name

    async def _on_startup(self) -> None:
        """On startup."""
        self._log.info("Starting up...")
        for agent_name in self._discover_agents():
            assert agent_name not in self._agent_processes, "Agent already running"
            self._log.info("Loading agent: %s", agent_name)
            auth = {
                "agent": agent_name,
                "token": uuid4().hex,
            }
            self._agents[agent_name] = {"auth": auth}
            agent_process = multiprocessing.Process(
                target=start_agent,
                args=(agent_name, f"http://{self.host}:{self.port}/", self.debug, auth),
            )
            agent_process.start()
            self._agent_processes[agent_name] = agent_process

    async def _on_shutdown(self) -> None:
        """On shutdown."""
        self._log.info("Shutting down...")
        await self.stop()

    async def _on_connect(self, sid: str, _environ: dict, auth: dict) -> None:
        """On connect."""
        self._log.info("Client connected: %s %s", sid, auth)
        if auth.get("token") != self._agents.get(auth.get("agent"), {}).get("auth", {}).get("token"):
            self._log.info("Client authentication failed: %s", sid)
            await self._sio.disconnect(sid=sid, namespace="/")
            return

    async def _on_disconnect(self, sid: str) -> None:
        """On disconnect."""
        self._log.info("Client disconnected: %s", sid)

    async def _on_event(self, kind: str, sid: str, frame: dict) -> None:
        """On event."""
        frame["timestamp"] = await self._get_timestamp()
        await self._sio.emit(kind, frame, skip_sid=sid, namespace="/")
        self._log.info("Client event: %s %s %s", sid, kind, frame)

    async def _get_timestamp(self) -> str:
        """Get timestamp."""
        return datetime.now().isoformat()

    async def _http_index(self) -> str:
        """Home page."""
        return await render_template("index.html", agents=self._agents)

    async def start(  # pylint: disable=arguments-differ
        self, host: str, port: int
    ) -> None:
        """Start the server."""
        self.host = host
        self.port = port
        self._log = self._init_log(name=self.name, debug=self.debug)
        self._log.info("Starting server...")
        self._start_scheduler()
        uvconfig = uvicorn.Config(
            self._sio_app,
            host=self.host,
            port=self.port,
            log_level="debug" if self.debug else "info",
        )
        server = uvicorn.Server(config=uvconfig)
        try:
            await server.serve()
        except KeyboardInterrupt:
            self._log.info("Shutting down server...")
        finally:
            await self.stop()
            self._log.info("Server stopped.")

    async def stop(self) -> None:
        """Stop the server."""
        self._log.info("Stopping server...")
        for name, process in self._agent_processes.items():
            self._log.info("Stopping agent: %s", name)
            process.terminate()
            process.join()
