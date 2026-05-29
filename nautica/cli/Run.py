from . import cli, click

import os
from colorama import Fore

from ..ext.Static import banner

from ..manager import Logger, LogLevel
from ..manager.config import ROOT_CONFIGS

from ..services import Services

@cli.command()
@click.argument("path", type=str, default=".", required=False)
def run(path: str = "."):
    print(f"{Fore.BLUE}{banner()}{Fore.RESET}")

    Logger.info("Validating project configuration...")    
    for path in ROOT_CONFIGS.values():
        if not os.path.exists(path):
            Logger.error(f"Project config '{path}' is missing!")
            return
        
    Services.ImportAll()
    Services.onStart()