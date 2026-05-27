from . import cli

import os
from colorama import Fore

from ..ext.Static import banner

from ..manager import Logger, LogLevel
from ..manager.config import ROOT_CONFIGS

from ..services import Registry

@cli.command(aliases=["i"])
def install():
    print(f"{Fore.BLUE}{banner()}{Fore.RESET}")

    Logger.info("Validating project configuration...")    
    for path in ROOT_CONFIGS.values():
        if not os.path.exists(path):
            Logger.error(f"Project config '{path}' is missing!")
            return
    
    #add download sequence whenever i add package manager
    
    #install services
    Logger.info("Installing services...")
    
    Registry.ImportAll()
    Registry.onInstall()
    
    Logger.ok("Services Installed")
    
    Logger.table() \
        .labels(["Services Installed"]) \
        .display(LogLevel.DEBUG)