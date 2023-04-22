"""
Zygote Discovery via mDNS.
"""
import socket
from zeroconf import IPVersion
from zeroconf.asyncio import AsyncServiceInfo, AsyncZeroconf

from zycelium.zygote.logging import get_logger


class LocalDNS:
    """Local DNS discovery."""

    def __init__(self):
        """Initialize."""
        self.logger = get_logger(__name__)
        self.zeroconf = AsyncZeroconf(ip_version=IPVersion.All)
        self.service = None

    async def start(
        self,
        domain: str,
        host: str,
        port: int,
    ):
        """Start mDNS."""
        ipv4_address = socket.gethostbyname(host)
        ipv6_address = socket.getaddrinfo(host, port, socket.AF_INET6)[0][4][0]
        self.logger.info("Starting Local DNS")
        try:
            self.service = AsyncServiceInfo(
                type_="_https._tcp.local.",
                name=f"{domain}._https._tcp.local.",
                addresses=[
                    socket.inet_aton(ipv4_address),
                    socket.inet_pton(socket.AF_INET6, ipv6_address),
                ],
                properties={"path": "/"},
                server=f"{domain}.local.",
                port=port,
            )
            await self.zeroconf.async_register_service(self.service)
            self.logger.info("Started Local DNS")
        except Exception as exc:  # pylint: disable=broad-except
            self.logger.exception("Unable to start Local DNS.", exc_info=exc)

    async def stop(self):
        """Stop mDNS."""
        if self.service:
            self.logger.info("Stopping Local DNS")
            await self.zeroconf.async_unregister_service(self.service)
            self.logger.info("Stopped Local DNS")
        await self.zeroconf.async_close()
