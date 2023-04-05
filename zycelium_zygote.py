"""Zygote App"""
import asyncio
import multiprocessing
import webbrowser

import rumps

from zycelium.zygote.server import Server


def _start_server(host: str, port: int, debug: bool = False):
    """Start server"""
    try:
        server = Server(name="zygote", debug=debug)
        asyncio.run(server.start(host=host, port=port))
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass


class ZygoteApp:
    """Zygote App"""

    def __init__(self, host: str, port: int, debug: bool = False):
        self.host = host
        self.port = port
        self.debug = debug
        self.process = None

    def start_server(self, sender):
        """Start server"""
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process = None
            sender.title = "Start Server"
            return
        self.process = multiprocessing.Process(
            target=_start_server, args=(self.host, self.port, self.debug)
        )
        self.process.start()
        sender.title = "Stop Server"

    def open_browser(self, _sender):
        """Open browser"""
        if self.process and self.process.is_alive():
            webbrowser.open(f"http://{self.host}:{self.port}/")
        else:
            rumps.alert("Server not running", "Please start the server.")

    def quit(self, _sender):
        """Quit"""
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join()
        rumps.quit_application()

    def run(self):
        """Run app"""
        app = rumps.App("Zygote", quit_button=None)
        app.icon = "images/icon.png"
        app.menu = [
            rumps.MenuItem("Open Browser", callback=self.open_browser),
            rumps.separator,
            rumps.MenuItem("Start Server", callback=self.start_server),
            rumps.separator,
            rumps.MenuItem("Quit", callback=self.quit),
        ]
        app.run()


def main():
    """Main"""
    app = ZygoteApp(host="localhost", port=3965, debug=True)
    app.run()


if __name__ == "__main__":
    main()
