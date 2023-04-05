"""This is a docstring for zycelium_zygote.py."""
import rumps


@rumps.clicked("Testing")
def tester(sender):
    """This is a callback for the "Testing" menu item"""
    sender.state = not sender.state


class SomeApp(rumps.App):
    """This is a docstring for SomeApp."""

    def __init__(self):
        super().__init__(type(self).__name__, menu=["On", "Testing"])
        rumps.debug_mode(True)
        self.icon = "images/icon.png"

    @rumps.clicked("On")
    def button(self, sender):
        """This is a callback for the "On" menu item"""
        sender.title = "Off" if sender.title == "On" else "On"
        rumps.Window("I can't think of a good example app...").run()


if __name__ == "__main__":
    SomeApp().run()
