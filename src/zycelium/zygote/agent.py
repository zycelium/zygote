"""
Agent.
"""
import socketio
from zycelium.zygote.logging import get_logger


class Agent:
    """Agent."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.spaces = {}
        self.log = get_logger("zygote.agent")
        self.sio = socketio.AsyncClient(ssl_verify=False)
        self.on = self.sio.on  # pylint: disable=invalid-name
        self.sio.on("command", self._on_command)

    async def connect(self, url: str, auth: dict) -> None:
        """Connect to server."""
        await self.sio.connect(url, auth=auth)

    async def disconnect(self) -> None:
        """Disconnect from server."""
        await self.sio.disconnect()

    async def emit(self, name: str, data: dict) -> None:
        """Emit event."""
        frame = {"name": name, "data": data}
        await self.sio.emit("event", frame)

    async def _on_command(self, data: dict) -> None:
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
        else:
            self.log.warning("Unknown command: %s", command)

    async def run(self, url: str, auth: dict) -> None:
        """Run agent."""
        try:
            self.log.info("Connecting to %s", url)
            await self.connect(url, auth=auth)
        except socketio.exceptions.ConnectionError:
            self.log.fatal("Connection error: check network connection, url or auth.")
        finally:
            await self.sio.wait()
