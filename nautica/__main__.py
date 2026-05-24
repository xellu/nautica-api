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
    
    try:
        from .services import Registry
        Registry.ImportAll()
        Registry.onStart()
    except Exception as e:
        from .manager import Logger
        Logger.trace(e)
    
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
    from .ext.Static import GitIgnore, ProjectExample
    
    for f in [".logs", "config", "plugins", "src/http"]:
        os.makedirs(f, exist_ok=True)
        
    Config.New("nautica",
        ConfigBuilder()
            .add("nautica.debug", True, "Enables tools and endpoints useful of debugging")
            .add("nautica.systemd", False, "Disables the shell service in order to work as a systemd service (Remote Access may be needed)")
            .build()
    )
    
    with open(".gitignore", "w") as f: f.write(GitIgnore)
    with open("src/http/+root.py", "w") as f: f.write(ProjectExample)
    
    
    os.chdir("..")
    if os.path.exists(".logs"):
        rmDir(".logs")
    
    print("Project created! Get started by running:")
    print(f"* cd {name}")
    print("nautica run")

if __name__ == "__main__":
    cli()