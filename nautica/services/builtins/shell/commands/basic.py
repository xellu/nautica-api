from ..decorator import RegisterCommand, CommandRequirements, ShellCommand
from .....services import Services
from .....manager import Logger, Config
from .....models.Requirements import AnyOf, Requirement

import colorama
import os

class ManualAutoOptions(AnyOf):
    def __init__(self):
        Requirement.__init__(self) #dont run AnyOf init

    @property
    def options(self):
        return list(Services["Shell"].handlers.keys())
    
    def __str__(self):
        return "command"

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
    s: dict[str, ShellCommand] = Services.get("Shell")
    if not s:
        Logger.error("Unable to get shell service, commands unavailable")
        return
    
    Logger.info(f"All available commands ({len(s.handlers.values())}):")
    for cmd in s.handlers.values():
        Logger.info(f" * {cmd.getUsage()} // {cmd.description}")
        
    Logger.info("To get more details about a command use 'man <command>'")
    
@RegisterCommand(
    "man", "Shows details about a command",
    args = CommandRequirements(
        args = {"command": ManualAutoOptions()}
    )
)
def manual(command: str = None):
    from .. import Shell
    
    s: Shell = Services.get("Shell")
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
    if value == Config("shell")["gui.enabled"]:
        Logger.error(f"Already selected")
        return

    Config("shell")["gui.enabled"] = value
    Logger.ok(f"Switched to {'GUI' if value else 'Terminal'}, restart for changes to take effect.")
  
@RegisterCommand(
    "lsserv", "Lists all services",
    CommandRequirements(
        flags = ["installOrder", "bootOrder"]
    )
)
def listServices(installOrder: bool = False, bootOrder: bool = False):
    order = (Services.instances, "Default Order")

    if installOrder:
        order = (Services._prioritize(sorted(Services.instances, key=lambda s: s._getName())), "Install Order")
    elif bootOrder:
        order = (Services._topoSort(Services._prioritize(Services.instances)), "Boot Order")

    Logger.info(f"Showing all {len(order[0])} services ({order[1]}):")
    for s in order[0]:
        Logger.info(f" * {s._getName()} {'[ONLINE]' if s.isEnabled() else f'[OFFLINE]'}")

@RegisterCommand("ram", "Shows ram usage")
def ramUsage():
    import psutil
    
    p = psutil.Process()
    Logger.info(f"RAM Usage: {p.memory_info().rss/1024/1024:.1f}MB")
    
@RegisterCommand("clearlogs", "Delete all log files (only in debug mode)")
def clearLogs():
    if not Config("nautica")["nautica.debug"]:
        Logger.error("This command is disabled in production")
        return
    
    from .....ext.Static import log_file
    from .....ext.Util import walkPath, rmFile
    from .....ext.Path import getRoot

    removed = 0
    for file in walkPath(getRoot(".logs")):
        if not file.endswith(".log"): continue
        if os.path.basename(file) == log_file: continue #skip current file

        ok, _, _ = rmFile(file)
        if not ok:
            Logger.error(f"Failed to remove '{file}'")
            continue
        
        removed += 1
        
    Logger.ok(f"Removed {removed} log files")