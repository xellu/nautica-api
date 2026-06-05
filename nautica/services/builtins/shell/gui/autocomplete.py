from textual.app import ComposeResult
from textual.containers import Container

from textual.widgets import Input, OptionList
from textual.widgets.option_list import Option

from textual import on

from .....services import Services
from .....models.Requirements import AnyOf

class CommandInput(Container):
    def __init__(self, gui):
        super().__init__()
        self.page = gui
    
    def compose(self) -> ComposeResult:
        yield Input(id="cmd-input", placeholder="Send a command")
    
    def on_mount(self):
        self._last_value = ""
    
    def get_suggestions(self, value: str) -> list[str]:
        s = Services.get("Shell")
        if not s: return []
        
        parts = value.split(" ")
        command = parts[0]
        
        if len(parts) == 1:
            return [
                name for name in s.handlers.keys()
                if name.lower().startswith(command.lower())
                and name.lower() != command.lower()
            ]
        
        handler = s.handlers.get(command)
        if not handler: return []
        
        last = parts[-1]
        
        #flags
        if last.startswith("--"):
            flag_input = last[2:]
            return [
                f"--{flag}" for flag in handler.arguments.flags
                if flag.lower().startswith(flag_input.lower())
                and flag.lower() != flag_input.lower()
            ]
        
        #arguments
        req_args = list(handler.arguments.args.items())
        if not req_args: return []
        
        typed_args = [p for p in parts[1:] if p and not p.startswith("--")]
        arg_index = len(typed_args) if last == "" else len(typed_args) - 1
        
        if arg_index < 0 or arg_index >= len(req_args):
            return []
        
        _, validator = req_args[arg_index]
        
        if isinstance(validator, AnyOf):
            options = [str(o) for o in validator.options]
        elif validator is bool:
            options = ["true", "false"]
        else:
            return []
        
        prefix = "" if last == "" else last
        return [o for o in options if o.lower().startswith(prefix.lower()) and o.lower() != prefix.lower()]
    
    def apply_suggestion(self, suggestion: str) -> None:
        input_widget = self.page.query_one("#cmd-input", Input)
        parts = input_widget.value.split(" ")
        
        if len(parts) == 1:
            input_widget.value = suggestion
        else:
            input_widget.value = " ".join(parts[:-1]) + " " + suggestion
        
        input_widget.cursor_position = len(input_widget.value)
        self.page.query_one("#suggestions").display = False
    
    @on(Input.Changed, "#cmd-input")
    def handle_input_changed(self, event: Input.Changed) -> None:
        suggestions = self.get_suggestions(event.value)
        widget = self.page.query_one("#suggestions", OptionList)
        
        widget.clear_options()
        
        if not suggestions or not event.value:
            widget.display = False
            return
        
        for s in suggestions:
            widget.add_option(Option(s, id=s))
        
        widget.display = True
    
    @on(Input.Submitted, "#cmd-input")
    def handle_submitted(self, event: Input.Submitted) -> None:
        self.page.query_one("#suggestions").display = False