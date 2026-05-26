from ..decorator import RegisterCommand, CommandRequirements, ShellCommand
from .....services import Services
from .....manager import Logger, Config
from .....models.Requirements import AnyOf

import os

@RegisterCommand(
    "stop", "Stops all services and exits",
    args = CommandRequirements(
        flags = ["force"]
    )
)
def stop(force: bool = False):
    if not force:        
        from ..gui import GUI
        if GUI.is_running:
            Logger.error("Use CTRL+Q to exit")
            return
        
        Services.onClose("requested by user")
        return
    
    os._exit(1)
    
@RegisterCommand(
    "help", "Shows all available commands",
)
def _help(command: str | None = None):
    s: dict[str, ShellCommand] = Services.Get("Shell")
    if not s:
        Logger.error("Unable to get shell service, commands unavailable")
        return
    
    Logger.info(f"All available commands ({len(s.handlers.values())}):")
    for cmd in s.handlers.values():
        Logger.info(f" * {cmd.getUsage()}")
    Logger.info("To get more details about a command use 'man <command>'")
    
@RegisterCommand(
    "man", "Shows details about a command",
    args = CommandRequirements(
        args = {"command": str}
    )
)
def manual(command: str = None):
    from .. import Shell
    
    s: Shell = Services.Get("Shell")
    if not s:
        Logger.error("Unable to get shell service, commands unavailable")
        return
    
    cmd: ShellCommand | None = None
    for handler in s.handlers.values():
        if handler.name.lower() == command.lower():
            cmd = handler
    
    if not cmd:
        Logger.error("Command not found")
        return
    
    Logger.info(f"Showing manual for '{cmd.name}'")
    Logger.info(cmd.description)
    Logger.info("Usage:")
    Logger.info(f" * {cmd.getUsage()}")

@RegisterCommand(
    "usegui", "Switches shell rendering options",
    CommandRequirements(
        args = {"value": bool}
    )
)
def useGui(value: bool):    
    if value == Config("nautica")["shell.gui"]:
        Logger.error(f"Already selected")
        return

    Config("nautica")["shell.gui"] = value
    Logger.ok(f"Switched to {'GUI' if value else 'Terminal'}, restart for changes to take effect.")
  
@RegisterCommand(
    "slist", "Lists all services"
)
def listServices():
    Logger.info("Showing all active services:")
    for s in Services.instances:
        Logger.info(f" * {s._getName()}")
