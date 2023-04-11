"""
Agent.
"""
import socketio


class Agent:
    """Agent."""
    def __init__(self, name: str) -> None:
        self.name = name
        self.sio = socketio.AsyncClient(ssl_verify=False)
        self.on = self.sio.on  # pylint: disable=invalid-name
    
    async def connect(self, url: str) -> None:
        """Connect to server."""
        await self.sio.connect(url)
    
    async def disconnect(self) -> None:
        """Disconnect from server."""
        await self.sio.disconnect()
    
    async def emit(self, event: str, data: dict) -> None:
        """Emit event."""
        await self.sio.emit(event, data)
    
    async def run(self, url: str) -> None:
        """Run agent."""
        await self.connect(url)
        await self.sio.wait()
