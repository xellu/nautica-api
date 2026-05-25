from ....models.Shell import ShellCommand, CommandRequirements
from ....services import Services

def RegisterCommand(
    name: str,
    description: str | None = None,
    args: CommandRequirements | None = None
):
    def decorator(func):
        Services.Get("Shell").handlers[name] = ShellCommand(
            name,
            func,
            
            description = description,
            arguments = args,
        )
        return func
    return decorator