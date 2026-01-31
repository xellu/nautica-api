class CommandDescriptor:
    def __init__(self):
        self.commands = {}

    def __call__(self, name: str, description: str, usage: str):
        def decorator(func):
            from .shared import ShellBus
            
            data = {
                "name": name,
                "description": description,
                "usage": usage,
                "func": func
            }
            self.commands[name] = data
            ShellBus.on(name)(func)
            
            return func
        return decorator
    
ShellCommand = CommandDescriptor()