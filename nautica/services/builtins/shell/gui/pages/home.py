from textual.containers import Container, VerticalScroll, HorizontalGroup
from textual.widgets import Static, Input, Checkbox
from textual import on

from ......manager import Logger, LogMemory
from ......services import Services

TABLE_ROWS = [
    ("Time", "Module", "Level", "Content")
]

class HomePage(Container):    
    def compose(self):               
        yield VerticalScroll(id="log")
        
        with HorizontalGroup(id="log-footer"):
            yield Input(id="log-input", placeholder="Send a command")
            yield Checkbox("Auto Scroll", value=True, id="log-autoscroll")
        
    def on_mount(self):
        self.mirror = LogMemory.CreateMirror()
        self.autoScroll = True
        
        self.set_interval(0.25, self.refresh_logs)
        self.query_one("#log-input", Input).focus()
        # self.query_one("#log-container", Container).border_title = "Log History"
    
    def refresh_logs(self) -> None:
        
        entries = self.mirror.Recall()
        self.mirror.Forget()

        widget = self.query_one("#log", VerticalScroll)        
        for log in entries:
            widget.mount(
                HorizontalGroup(
                    Static(log["timestamp"]["formatted"], classes="log-timestamp"),
                    Static(f"{log['level']}", classes=f"log-level log-level-{log['level'].lower()}"),
                    Static(".".join(
                        [part.capitalize() for part in log["moduleName"]["short"].split(".")]    
                    ), classes=f"log-level-{log['level'].lower()} log-module"),
                    Static(log["message"], classes="log-message")
                )
            )
            # widget.write(f"{log['message']}")
            
        if self.autoScroll:
            widget.scroll_end(animate=False)

        # Logger.ok(f"Wrote: {len(entries)}") #dont uncomment unless u want to brick yourself

    @on(Checkbox.Changed, "#log-autoscroll")
    def handle_autoscroll(self, event: Checkbox.Changed):
        self.autoScroll = event.checkbox.value
        
    @on(Input.Submitted, "#log-input")
    async def handle_run_command(self, event: Input.Submitted):
        event.input.value = ""

        if event.value:
            s = Services.Get("Shell")
            if not s:
                Logger.error(f"Shell service not found")
                return
            
            ok, res = await s.run_command(event.value)
            if not ok:
                Logger.error(f"Command failed to execute: {res}")
                return

            if res: Logger.ok(res)
            