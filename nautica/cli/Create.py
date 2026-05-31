from . import cli, click

import os
from colorama import Fore

from ..ext.Static import banner, GitIgnore, ProjectExample
from ..ext.Util import walkPath

from ..manager import Logger, LogLevel

from ..services import Registry

@cli.command()
@click.argument("name", type=str)
def create(name):
    _create(name)
    
    Logger.table() \
        .labels(["Project Created! Get Started by running:"]) \
        .row([f"cd {name}"]).row(["nautica install"]).row(["nautica run ."]) \
        .row([""]).row(["Thank you for using Nautica3!"]) \
        .display(LogLevel.INFO)
    
def _create(name):
    # print(f"{Fore.BLUE}{banner()}{Fore.RESET}")
    if os.path.exists(name) and len(walkPath(name, include_dirs=True)) > 0:
        Logger.error(f"A Non-empty directory with this name already exists")
        return
    
    #prep working directory
    Logger.info("Creating project directories...")
    os.makedirs(name, exist_ok=True)
    prev_dir = os.path.abspath(os.curdir)

    os.chdir(name)
    
    for f in [".logs", "config", "plugins", "src/http"]:
        os.makedirs(f, exist_ok=True)

    with open(".gitignore", "w") as f: f.write(GitIgnore)
    with open("src/http/+root.py", "w") as f: f.write(ProjectExample)    

    Logger.ok("Created project tree")
    
    #install services
    Logger.info("Installing services...")
    
    Registry.ImportAll()
    Registry.onInstall()
        
    #clean up
    os.chdir(prev_dir)