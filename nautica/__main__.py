from . import _run
from .manager import Config, ConfigBuilder
from .ext.Util import rmDir

import os
import click

@click.group()
def cli(): ...

@cli.command()
def run():
    if _run() is False:
        return
    
    from .services import Registry
    Registry.ImportAll()
    Registry.onStart()
    
@cli.command()
def load():
    for f in ["config", "plugins"]:
        os.makedirs(f, exist_ok=True)
        
    Config.New("nautica",
        ConfigBuilder()
            .add("nautica.debug", True, "Enables tools and endpoints useful of debugging")
            .add("nautica.systemd", False, "Disables the shell service in order to work as a systemd service (Remote Access may be needed)")
            .build()
    )
    
@cli.command()
@click.argument("name", type=str)
def create(name):
    if os.path.exists(name):
        return print("A directory with this name already exists")
    
    os.makedirs(name)
    os.chdir(name)
    from .ext.Static import GitIgnore
    
    for f in [".logs", "config", "plugins", "src"]:
        os.makedirs(f, exist_ok=True)
        
    Config.New("nautica",
        ConfigBuilder()
            .add("nautica.debug", True, "Enables tools and endpoints useful of debugging")
            .add("nautica.systemd", False, "Disables the shell service in order to work as a systemd service (Remote Access may be needed)")
            .build()
    )
    
    with open(".gitignore", "w") as f: f.write(GitIgnore)
    
    os.chdir("..")
    if os.path.exists(".logs"):
        rmDir(".logs")
    
    print("Project created! Get started by running:")
    print(f"* cd {name}")
    print("nautica run")

if __name__ == "__main__":
    cli()