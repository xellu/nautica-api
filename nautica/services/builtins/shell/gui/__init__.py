from textual.app import App, ComposeResult
from textual import events
from textual.widgets import RichLog

from .....manager import Config

from .themes import frostTheme, catppuccinTheme

class N3GUI(App):        
    def on_mount(self) -> None:
        theme = Config("nautica")["shell.guiTheme"]
        if theme not in ["frost", "catppuccin", "nord", "gruvbox", "tokyo-night", "textual-dark", "solarized-light", "atom-one-dark", "atom-one-light"]:
            theme = "frost"
    
        self.register_theme(frostTheme)
        self.register_theme(catppuccinTheme)
        self.theme = theme
    
    # def compose(self) -> ComposeResult:
    #     # self.exit()
    #     yield RichLog()

    def on_key(self, event: events.Key) -> None:
        ...
        
GUI = N3GUI()