from textual.suggester import Suggester

class ShellSuggester(Suggester):
    def __init__(self):
        super().__init__(case_sensitive=False)
    
    async def get_suggestion(self, value: str) -> str | None:
        from .....services import Services
        from .....models.Requirements import AnyOf
        import builtins
        
        s = Services.Get("Shell")
        if not s: return None
        
        parts = value.split(" ")
        command = parts[0]
        
        #suggest command names
        if len(parts) == 1:
            matches = [
                name for name in s.handlers.keys()
                if name.lower().startswith(command.lower())
                and name.lower() != command.lower()
            ]
            return matches[0] if matches else None
        
        #get handler
        handler = s.handlers.get(command)
        if not handler: return None
        
        last = parts[-1]
        
        #suggesting flags (--flag)
        if last.startswith("--"):
            flag_input = last[2:]
            matches = [
                f"--{flag}" for flag in handler.arguments.flags
                if flag.lower().startswith(flag_input.lower())
                and flag.lower() != flag_input.lower()
            ]
            if matches:
                return " ".join(parts[:-1]) + " " + matches[0]
            return None
        
        #suggesting argument values
        req_args = list(handler.arguments.args.items())
        if not req_args: return None
        
        #count already typed args
        typed_args = [p for p in parts[1:] if p and not p.startswith("--")]
        
        #if last part is empty, suggest next arg
        #if last part is not empty, suggest completion for current arg
        if last == "":
            arg_index = len(typed_args)
        else:
            arg_index = len(typed_args) - 1
        
        if arg_index < 0 or arg_index >= len(req_args):
            return None
        
        arg_name, validator = req_args[arg_index]
        
        #get options based on validator type
        if isinstance(validator, AnyOf):
            options = [str(o) for o in validator.options]
        elif validator is builtins.bool:
            options = ["true", "false"]
        else:
            return None
        
        #filter options
        prefix = "" if last == "" else last
        matches = [
            opt for opt in options
            if opt.lower().startswith(prefix.lower())
            and opt.lower() != prefix.lower()
        ]
        
        if not matches: return None
        
        if last == "":
            return value + matches[0]
        else:
            return " ".join(parts[:-1]) + " " + matches[0]