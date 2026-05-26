from textual.containers import Container, VerticalScroll, HorizontalGroup
from textual.widgets import Static, Input, Checkbox, DataTable
from textual.widgets.data_table import RowKey

from textual import on


import threading

from ......manager import Logger, LogMemory, Config
from ......services import Services

TABLE_ROWS = [
    ("Time", "Module", "Level", "Content")
]

class HomePage(Container):    
    def compose(self):               
        with HorizontalGroup(id="home-container"):
            yield VerticalScroll(id="log")
            yield DataTable(id="threads")
        
        with HorizontalGroup(id="log-footer"):
            yield Input(id="log-input", placeholder="Send a command")
            yield Checkbox("Auto Scroll", id="log-autoscroll", classes="checkbox-sm")
            yield Checkbox("Threads", id="home-threads", classes="checkbox-sm")
        
    def on_mount(self):
        self.mirror = LogMemory.CreateMirror()
        self.autoScroll = Config("shell-gui")("home.logScroll")
        
        #logs
        self.query_one("#log-input", Input).focus()
        self.query_one("#log-autoscroll", Checkbox).value = self.autoScroll
        
        #threads
        self._thread_keys: dict[int, RowKey] = {}
        self.query_one("#threads", DataTable).add_columns("Name", "Func", "Module")
        self.query_one("#threads").styles.display = "block" if Config("shell-gui")["home.threadList"] else "none"

        
        self.set_interval(0.25, self.refresh_logs)
        self.set_interval(1, self.refresh_threads)

    
    def refresh_threads(self) -> None:
        widget = self.query_one("#threads", DataTable)
        current = {t.ident: t for t in threading.enumerate()}

        widget.border_title = "Threads"
        widget.border_subtitle = f"{len(current.keys())} Active"

        #clear threads
        for ident in list(self._thread_keys):
            if ident not in current:
                widget.remove_row(self._thread_keys.pop(ident))

        #add & update threads
        for ident, t in current.items():
            func = t._target.__name__ if t._target else str(t.ident)
            module = t._target.__module__ if t._target else "N/A"

            if ident not in self._thread_keys:
                key = widget.add_row(t.name, func, module, key=str(ident))
                self._thread_keys[ident] = key
        
    def refresh_logs(self) -> None:
        
        entries = self.mirror.Recall()
        if not entries: return
        
        self.mirror.Forget()
        
        widget = self.query_one("#log", VerticalScroll)    
        widget.border_title = f"Console"
        widget.border_subtitle = f"{len(LogMemory) if len(LogMemory) <= LogMemory.limit else str(LogMemory.limit) + '+'} Entries"
        
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
        Config("shell-gui")["home.logScroll"] = self.autoScroll
        
    @on(Checkbox.Changed, "#home-threads")
    def handle_threads_toggle(self, event: Checkbox.Changed):
        self.query_one("#threads").styles.display = "block" if event.value else "none"
        
    @on(Input.Submitted, "#log-input")
    async def handle_run_command(self, event: Input.Submitted):
        event.input.value = ""
        
        if event.value == "clear":
            self.query_one("#log", VerticalScroll).remove_children("*")
            return

        if event.value:
            s = Services.Get("Shell")
            if not s:
                Logger.error("Shell service not found")
                return
            
            ok, res = await s.run_command(event.value)
            if not ok:
                Logger.error(f"Command failed to execute: {res}")
                return

            if res: Logger.ok(res)
            