"""
Zygote server agent.
"""
import importlib
import pkgutil
from typing import Iterable
import socketio
import uvicorn
from quart import Quart
from quart_cors import cors

from zycelium.zygote.agent import Agent


class Server(Agent):
    """Zygote server agent."""

    def __init__(
        self, name: str, debug: bool = False, *, allow_origin: str = "*"
    ) -> None:
        self.host = ""
        self.port = 0
        self._allow_origin = allow_origin
        super().__init__(name=name, debug=debug)
        self._quart_app = Quart(self.name)
        self._quart_app = cors(self._quart_app, allow_origin=self._allow_origin)
        self._quart_app.config["DEBUG"] = self.debug
        self._sio_app = socketio.ASGIApp(self._sio, self._quart_app)
        self._quart_app.before_serving(self._on_startup)
        self._quart_app.after_serving(self._on_shutdown)

    def _init_sio(self) -> socketio.AsyncServer:
        sio = socketio.AsyncServer(
            async_mode="asgi", cors_allowed_origins=self._allow_origin
        )
        return sio

    def _discover_agents(self) -> Iterable[str]:
        """Discover agents."""
        self._log.info("Discovering agents...")

        def _iter_namespace(ns_pkg):
            return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

        # Built-in agents
        namespace = importlib.import_module("zycelium.zygote.agents")
        for _, name, _ in _iter_namespace(namespace):
            self._log.info("Found agent: %s", name)
            yield name
    
    async def _on_startup(self) -> None:
        """On startup."""
        self._log.info("Starting up...")
        for agent in self._discover_agents():
            self._log.info("Loading agent: %s", agent)

    async def _on_shutdown(self) -> None:
        """On shutdown."""
        self._log.info("Shutting down...")

    async def start(  # pylint: disable=arguments-differ
        self, host: str, port: int
    ) -> None:
        """Start the server."""
        self.host = host
        self.port = port
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
        self._stop_scheduler()