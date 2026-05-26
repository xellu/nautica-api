from textual.containers import Container, VerticalScroll, HorizontalGroup, VerticalGroup
from textual.widgets import Static, Input, Checkbox, DataTable, OptionList
from textual.widgets.data_table import RowKey

from textual import on


import threading
import asyncio

from ......manager import Logger, LogMemory, Config
from ......services import Services
from ..autocomplete import CommandInput

TABLE_ROWS = [
    ("Time", "Module", "Level", "Content")
]

class HomePage(Container):    
    def compose(self):       
        with HorizontalGroup(id="home-container"):
            yield VerticalScroll(id="log")
            with VerticalGroup(id="thread-container"):
                yield DataTable(id="threads")
                yield DataTable(id="threadsAsync")
        
        
        with HorizontalGroup(id="log-footer"):
            yield CommandInput(self)
            yield Checkbox("Auto Scroll", id="log-autoscroll", classes="checkbox-sm")
            yield Checkbox("Threads", id="home-threads", classes="checkbox-sm")
            
        yield OptionList(id="suggestions")
        
    def on_mount(self):
        self.mirror = LogMemory.CreateMirror()
        self.autoScroll = Config("shell-gui")("home.logScroll")
        
        #logs
        # self.query_one("#log-input", Input).focus()
        self.query_one("#log-autoscroll", Checkbox).value = self.autoScroll
        
        #threads
        self._thread_keys: dict[int, RowKey] = {}
        self._thread_workers_keys: dict[str, RowKey] = {}
        self.query_one("#threads", DataTable).add_columns("Name", "Func", "Module")
        async_cols = self.query_one("#threadsAsync", DataTable).add_columns("Func", "Module", "Count")
        self._async_count_col = async_cols[2]
        self.query_one("#thread-container").styles.display = "block" if Config("shell-gui")["home.threadList"] else "none"
        
        self.set_interval(0.25, self.refresh_logs)
        self.set_interval(1, self.refresh_threads)

    
    async def refresh_threads(self) -> None:
        threadList = self.query_one("#threads", DataTable)
        asyncioList = self.query_one("#threadsAsync", DataTable)
        current = {t.ident: t for t in threading.enumerate()}
        hidden = 0

        

        # clear removed threads
        for ident in list(self._thread_keys):
            if ident not in current:
                threadList.remove_row(self._thread_keys.pop(ident))

        # add new threads
        for ident, t in current.items():
            func = t._target.__name__ if t._target else str(t.ident)
            module = t._target.__module__ if t._target else "N/A"
            
            if "asyncio" in t.name:
                hidden += 1
                continue
                
            if ident not in self._thread_keys:
                key = threadList.add_row(t.name, func, module, key=str(ident))
                self._thread_keys[ident] = key

        #asyncio tasks/workers, grouped by func name (for stacking)
        groups: dict[str, tuple[int, str]] = {}
        for t in asyncio.all_tasks():
            coro = t.get_coro()
            func = getattr(coro, "__qualname__", None) or getattr(coro, "__name__", "?")
            frame = getattr(coro, "cr_frame", None)
            module = frame.f_globals.get("__name__", "N/A") if frame else "N/A"
            count, _ = groups.get(func, (0, module))
            groups[func] = (count + 1, module)

        #update titles
        threadList.border_title = f"Threads"
        threadList.border_subtitle = f"{len(current)-hidden} Active (+{hidden} Worker Threads)"

        asyncioList.border_title = "Workers"
        asyncioList.border_subtitle = f"{sum(c for c, _ in groups.values())} Active"

        #update workers
        for func in list(self._thread_workers_keys):
            if func not in groups:
                asyncioList.remove_row(self._thread_workers_keys.pop(func))

        for func, (count, module) in groups.items():
            if func not in self._thread_workers_keys:
                key = asyncioList.add_row(func, module, f"{count}x", key=func)
                self._thread_workers_keys[func] = key
            else:
                asyncioList.update_cell(self._thread_workers_keys[func], self._async_count_col, f"{count}x")
        
    def refresh_logs(self) -> None:
        
        entries = self.mirror.Recall()
        if not entries: return
        
        self.mirror.Forget()
        
        widget = self.query_one("#log", VerticalScroll)    
        widget.border_title = f"Console"
        widget.border_subtitle = f"{len(LogMemory) if len(LogMemory) < LogMemory.limit else str(LogMemory.limit) + '+'} Records"
        
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
        self.query_one("#thread-container").styles.display = "block" if event.value else "none"
        
    @on(Input.Submitted, "#cmd-input")
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
            
    @on(OptionList.OptionSelected, "#suggestions")
    def handle_suggestion_selected(self, event: OptionList.OptionSelected):
        cmd = self.query_one(CommandInput)
        cmd.apply_suggestion(str(event.option.prompt))
        self.query_one("#cmd-input", Input).focus()