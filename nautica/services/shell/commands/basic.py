from ..descriptor import ShellCommand
from ..shared import logger, ShellBus

import os

@ShellCommand("help", "Shows command list or usage guides", "help [command]")
def help(command=None):
    if not command:
        logger.info("Command List:      <> - Required | [] - Optional")
        for _, cmd in ShellCommand.commands.items():
            logger.info(f"  {cmd['usage']} - {cmd['description']}")
        
        return

    cmd = ShellCommand.commands.get(command)
    if not cmd:
        logger.warn("Command not found")
    
    logger.info(f"About {str(command).capitalize()}:")
    for k, v in cmd.items():
        logger.info(f"  {k}: {v}")

@ShellCommand("stop", "Stops the server, use the 'force' flag to kill the server", "stop [--force]")
def shutdown(force=False):
    from .... import Core
    
    Core.Eventer.emit("shutdown" if not force else "shutdown.force")
    

@ShellBus.on("cls")
@ShellCommand("clear", "Clears the console output", "clear")
def clear():
    os.system("cls" if os.name == "nt" else "clear")