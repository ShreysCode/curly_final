import socket

from zeroconf import ServiceInfo
from zeroconf.asyncio import AsyncZeroconf


SERVICE_TYPE = "_curly._tcp.local."
SERVICE_NAME = "Curly LLM._curly._tcp.local."
SERVICE_PORT = 8000


class CurlyServiceDiscovery:
    """Advertise the local Curly HTTP service over mDNS."""

    def __init__(self):
        self.zeroconf = None
        self.service_info = None

    async def start(self):
        if self.zeroconf is not None:
            return

        local_ip = self._get_local_ip()

        self.zeroconf = AsyncZeroconf()

        self.service_info = ServiceInfo(
            SERVICE_TYPE,
            SERVICE_NAME,
            addresses=[socket.inet_aton(local_ip)],
            port=SERVICE_PORT,
            properties={
                "api": "curly",
                "version": "1.0",
            },
        )

        try:
            register_task = await self.zeroconf.async_register_service(
                self.service_info,
                allow_name_change=True,
            )

            if register_task is not None:
                await register_task

            print(
                "Curly mDNS service advertised: "
                f"{SERVICE_NAME} -> {local_ip}:{SERVICE_PORT}"
            )

        except Exception as error:
            print(
                "Curly mDNS advertisement failed: "
                f"{type(error).__name__}: {error}"
            )

            await self._close_safely()

    async def stop(self):
        await self._close_safely()

    async def _close_safely(self):
        zeroconf = self.zeroconf
        service_info = self.service_info

        self.zeroconf = None
        self.service_info = None

        if zeroconf is None:
            return

        try:
            if service_info is not None:
                unregister_task = await zeroconf.async_unregister_service(
                    service_info
                )

                if unregister_task is not None:
                    await unregister_task

        except Exception as error:
            print(
                "Curly mDNS unregister failed: "
                f"{type(error).__name__}: {error}"
            )

        finally:
            try:
                await zeroconf.async_close()

            except Exception as error:
                print(
                    "Curly mDNS close failed: "
                    f"{type(error).__name__}: {error}"
                )

    @staticmethod
    def _get_local_ip():
        """Return the local IPv4 address used for the default network route."""

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )

        try:
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]

        finally:
            sock.close()

        if not local_ip or local_ip.startswith("127."):
            raise RuntimeError(
                "Could not determine a LAN IPv4 address "
                f"(got {local_ip!r})"
            )

        return local_ip