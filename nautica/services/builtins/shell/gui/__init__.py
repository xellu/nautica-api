from textual.app import App, ComposeResult
from textual import events
from textual.widgets import RichLog, Static, Tabs, Tab, ContentSwitcher
from textual.containers import Container

from .....manager import Config
from .....ext.Static import RELEASE

from .themes import frostTheme, catppuccinTheme
from .css import TCSS
from .pages import (
    home
)

PAGES = [
    "overview",
    # "test"
]

class Header(Container):
    def compose(self):
        yield Tabs(*[Tab(page.capitalize(), id=f"nav-{page}") for page in PAGES])

class N3GUI(App):
    CSS = TCSS

    def on_mount(self) -> None:
        theme = Config("nautica")["shell.guiTheme"]
        if theme not in ["frost", "catppuccin", "nord", "gruvbox", "tokyo-night",
                         "textual-dark", "solarized-light", "atom-one-dark", "atom-one-light"]:
            theme = "frost"

        self.register_theme(frostTheme)
        self.register_theme(catppuccinTheme)
        self.theme = theme

        self.query_one("#header").border_title = f"[ Nautica v{RELEASE} ]"

    def compose(self) -> ComposeResult:
        yield Header(id="header")
        with ContentSwitcher(initial="page-overview"):
            yield home.HomePage(id="page-overview", classes="page")
            # yield home.HomePage(id="page-test", classes="page")

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        if event.tab and event.tab.id:
            page = event.tab.id[4:]  # strip "nav-"
            self.query_one(ContentSwitcher).current = f"page-{page}"
            # self.query_one("#mainPage").border_title = page.capitalize()

    def on_key(self, event: events.Key) -> None:
        ...


GUI = N3GUI()
