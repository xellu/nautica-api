from . import cli, click

import os
from colorama import Fore

from ..ext.Static import banner
from ..ext.Path import setRoot, getRoot

from ..manager import Logger, LogLevel
from ..manager.config import ROOT_CONFIGS

from ..services import Services

@cli.command()
@click.argument("path", type=str, default=".", required=False)
def run(path: str = "."):
    _run(path)
    
def _run(path):
    print(f"{Fore.BLUE}{banner()}{Fore.RESET}")

    setRoot(path)

    Logger.info("Validating project configuration...")    
    for path in ROOT_CONFIGS.values():
        if not os.path.exists(getRoot(path)):
            Logger.error(f"Project config '{path}' is missing!")
            return
        
        
    Services.importAll()
    Services.onStart()