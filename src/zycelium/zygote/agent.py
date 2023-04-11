"""
Agent.
"""
from typing import final
import socketio


class Agent:
    """Agent."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.sio = socketio.AsyncClient(ssl_verify=False)
        self.on = self.sio.on  # pylint: disable=invalid-name
        self.sio.on("connect", self.on_connect)
        self.sio.on("disconnect", self.on_disconnect)

    async def connect(self, url: str, auth: dict) -> None:
        """Connect to server."""
        await self.sio.connect(url, auth=auth)

    async def disconnect(self) -> None:
        """Disconnect from server."""
        await self.sio.disconnect()

    async def emit(self, event: str, data: dict) -> None:
        """Emit event."""
        await self.sio.emit(event, data)

    async def run(self, url: str, auth: dict) -> None:
        """Run agent."""
        try:
            await self.connect(url, auth=auth)
        except socketio.exceptions.ConnectionError:
            print("Connection error: check network connection, url or auth.")
        finally:
            await self.sio.wait()

    async def on_connect(self) -> None:
        """On connect."""
        print("Connected to server")

    async def on_disconnect(self) -> None:
        """On disconnect."""
        print("Disconnected from server")
