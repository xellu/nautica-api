from . import cli

import os
import click
import shutil

from ..manager import Logger, LogLevel, Config, ConfigBuilder

from ..services import Registry
from ..ext.Util import walkPath, rmDir, isGitIgnored
from ..ext.Static import PackageServiceExample, GitIgnore

def is_valid_name(name: str):
    for char in name:
        if char not in "abcdefghijklmnopqrstuvwxyz0123456789_-.":
            return False
    return True

@cli.group()
def packager():
    pass

@packager.command()
@click.argument("name", type=str)
def create(name: str):
    if os.path.exists(name) and len(walkPath(name, include_dirs=True)) > 0:
        Logger.error(f"A Non-empty directory with this name already exists")
        return
    
    #prep working directory
    Logger.info("Creating project directories...")
    os.makedirs(name, exist_ok=True)
    prev_dir = os.path.abspath(os.curdir)

    os.chdir(name)
    
    Config.New("projectdev", 
        ConfigBuilder()
            .add("name", os.path.basename(name), comment="This name will be used on the package registry; a-z0-9._-")
            .add("version", "1.0.0", comment="Project version, format: https://semver.org/")
            .add("dependsOn", [], comment="List of package names that are required to run this service. Services need to be available on package registry.")
            .add("pyPackages", [], comment="List of PyPI packages this service depends on.")
            .build()
    )
    with open("__init__.py", "w") as f:
        f.write(PackageServiceExample)
    with open(".gitignore", "w") as f:
        f.write(GitIgnore)
    
    Logger.ok("Created project structure")
    
    os.chdir(prev_dir)
    
    Logger.table() \
        .labels(["Package Created!"]) \
        .row([f"cd {name}"]) \
        .row(["And edit '__init__.py'"]) \
        .row([""]).row(["Get Started:"]) \
        .row([""]).row(["1. Creating Testing Environment:"]) \
        .row(["nautica packager testenv"]) \
        .row([""]).row(["2. Testing Your Service:"]) \
        .row(["nautica packager test"]) \
        .row([""]).row(["3. Publishing:"]) \
        .row(["nautica packager publish"]) \
        .display()
    
@packager.command()
def testenv():
    from .Create import _create
    
    if ".testenv" in os.listdir("."):
        Logger.info("Recreating the test environment...")
        rmDir(".testenv")
    
    _create(".testenv")
    Logger.table() \
        .labels(["Test Environment Created! To start it:"]) \
        .row(["nautica packager test"]).display()
        
@packager.command()
def test():
    if ".testenv" not in os.listdir("."):
        Logger.error("No test environment found. Run 'nautica packager testenv' to create one.")
        return
    
    if "__init__.py" not in os.listdir("."):
        Logger.error("No entry point found for your service, make sure __init__.py exists.")
        return
    
    prev_dir = os.path.abspath(os.curdir)
    
    #copy service package into plugins
    Config.New("projectdev", ConfigBuilder().build()) #init config
    name = Config("projectdev")["name"]
    
    if not is_valid_name(name):
        Logger.error(f"Project name contains invalid characters. Allowed: a-z0-9._-")
        return
        
    new_dir = os.path.join(".testenv", "plugins", name)

    def is_ignored(directory, files):
        return [f for f in files if isGitIgnored(os.path.join(directory, f))]

    if os.path.exists(new_dir):
        rmDir(new_dir) #clean previous tests
        
    #copy files
    shutil.copytree(".", new_dir, ignore=is_ignored)
    
    os.chdir(prev_dir)
    
    #run it
    from .Run import _run
    _run(".testenv")