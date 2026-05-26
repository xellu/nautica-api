from .Requirements import Requirement

class CommandRequirements:
    def __init__(self, args: dict[str, type | Requirement] = None, flags: list[str] = None):
        self.args = {}
        self.flags = set()
        
        if args: self.Arguments(args)
        if flags: self.Flags(flags)
                
    def Arguments(self, args: dict[str, type | Requirement]):
        if not isinstance(args, dict): raise TypeError("Unable to parse arguments")
        for k, v in args.items():
            if not (isinstance(v, type) or isinstance(v, Requirement)):
                raise TypeError(f"Unsupported argument type for '{k}'")

        self.args = args
        return self

    def Flags(self, flags: list[str]):
        if not isinstance(flags, list): raise TypeError("Unable to parse flags")

        self.flags = set(flags)
        return self

    def validate(self, args: list, flags: dict) -> tuple[bool, str]:
        req_args = list(self.args.items())
        if len(args) < len(req_args):
            names = ", ".join(f"<{n}>" for n in self.args)
            return False, f"Expected {len(req_args)} argument(s): {names}"

        for i, (name, validator) in enumerate(req_args):
            value = args[i]
            if isinstance(validator, Requirement):
                if not validator.isValid(value):
                    return False, f"Argument <{name}> does not match {str(validator)}"
            elif isinstance(validator, type):
                if not isinstance(value, validator) or (validator is bool and isinstance(value, int) and not isinstance(value, bool)):
                    try:
                        if validator is bool:
                            if isinstance(value, str):
                                if value.lower() in ("true", "1", "yes"):
                                    args[i] = True
                                elif value.lower() in ("false", "0", "no"):
                                    args[i] = False
                                else:
                                    return False, f"Argument <{name}> must be bool, got '{value}'"
                            else:
                                args[i] = bool(value)
                        else:
                            args[i] = validator(value)
                    except (ValueError, TypeError):
                        return False, f"Argument <{name}> must be {validator.__name__}, got '{value}'"

        for flag in flags:
            if self.flags and flag not in self.flags:
                return False, f"Unknown flag '--{flag}'"

        return True, ""

    

class ShellCommand:
    def __init__(self, name: str, func: callable, description: str | None = None, arguments: CommandRequirements | None = None):
        self.name: str = name
        self.func: callable = func
        
        self.description: str = description or "No description provided"
        self.arguments = CommandRequirements() if arguments is None else arguments
        
    def getUsage(self):
        out = f"{self.name}"
        #construct args
        for arg, _type in self.arguments.args.items():
            arg_type = "?"
            match type(_type).__name__:
                case "type":
                    arg_type = _type.__name__
                case "AnyOf":
                    arg_type = "'" + "|".join(_type.options) + "'"
                case "AnyTypeOf":
                    arg_type = "|".join([t.__name__ for t in _type.types])
                case _:
                    arg_type = str(_type)
        
            out += f" <{arg}: {arg_type}>"
            
        #construct flags
        for flag in self.arguments.flags:
            out += f" [--{flag}]"
            
        return out