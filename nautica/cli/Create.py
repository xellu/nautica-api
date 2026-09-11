from . import cli, click

import os
from colorama import Fore

from ..ext.Static import banner, GitIgnore, ProjectExample
from ..ext.LLMs import LLMS, AGENTS
from ..ext.Util import walkPath
from ..ext.Path import setRoot, getRoot

from ..manager import Logger, LogLevel, Config

from ..services import Registry

@cli.command()
@click.argument("name", type=str)
@click.option("--demo", "-d", is_flag=True)
def create(name, demo: bool = False):
    _create(name, demo)
    
    Logger.table() \
        .labels(["Project Created! Get Started by running:"]) \
        .row([f"cd {name}"]).row(["nautica install"]).row(["nautica run ."]) \
        .row([""]).row(["Thank you for using Nautica3!"]) \
        .display(LogLevel.INFO)
    
def _create(name, demo: bool = False):
    # print(f"{Fore.BLUE}{banner()}{Fore.RESET}")
    if os.path.exists(name) and len(walkPath(name, include_dirs=True)) > 0:
        Logger.error(f"A Non-empty directory with this name already exists")
        return
    
    Logger.info("Creating project directories...")
    os.makedirs(name, exist_ok=True)
    setRoot(os.path.abspath(name))

    for f in [".logs", "config", "plugins", "src/http", "src/lib"]:
        os.makedirs(getRoot(f), exist_ok=True)

    with open(getRoot(".gitignore"), "w", encoding="utf-8") as f: f.write(GitIgnore)

    with open(getRoot("DOCS.md"), "w", encoding="utf-8") as f: f.write(LLMS)
    with open(getRoot("AGENTS.md"), "w", encoding="utf-8") as f: f.write(AGENTS)
    with open(getRoot("CLAUDE.md"), "w") as f: f.write("@AGENTS.md")
    if demo: 
        with open(getRoot("src/http/+root.py"), "w", encoding="utf-8") as f: f.write(ProjectExample)

    Logger.ok("Created project tree")

    Logger.info("Installing services...")
    Registry.importAll()
    Registry.onInstall()
    
    if demo:
        Config("nautica")["services.http"] = True