from . import cli

import os
import click
import shutil
import requests
from zipfile import ZipFile
from platformdirs import user_data_dir

from ..manager import Logger, Config, ConfigBuilder
from ..services import Registry
from ..ext.Util import walkPath, rmDir, isGitIgnored, filterPathsGitIgnore
from ..ext.Static import PackageServiceExample, GitIgnore
from ..ext.StatusCodes import getMessage

from .PackageManagerAuth import prompt_login, login, get_all_regs, set_reg_url, get_reg_url


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
    
    #create config
    Config.New("projectdev", 
        ConfigBuilder()
            .add("name", os.path.basename(os.path.abspath(".")), comment="This name will be used on the package registry; a-z0-9._-")
            .add("version", "1.0.0", comment="Project version, format: https://semver.org/")
            .add("dependsOn", [], comment="List of package names that are required to run this service. Services need to be available on package registry.")
            .add("pyPackages", [], comment="List of PyPI packages this service depends on.")
            .build()
    )
    #create other files
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
        .row(["nautica packager envmake"]) \
        .row(["nautica packager envinstall"]) \
        .row([""]).row(["2. Testing Your Service:"]) \
        .row(["nautica packager test"]) \
        .row([""]).row(["3. Publishing:"]) \
        .row(["nautica packager publish"]) \
        .display()
    
@packager.command()
def envmake():
    from .Create import _create
    
    if ".testenv" in os.listdir("."): #delete old env
        Logger.info("Recreating the test environment...")
        rmDir(".testenv")
    
    #create env
    _create(".testenv")
    Logger.table() \
        .labels(["Test Environment Created! To install dependencies run:"]) \
        .row(["nautica packager envinstall"]).display()
        
@packager.command()
def envinstall():
    #project checks
    if ".testenv" not in os.listdir("."):
        Logger.error("No test environment found. Run 'nautica packager envmake' to create one.")
        return
    
    #install    
    prev_dir = os.path.abspath(os.curdir)

    os.chdir(".testenv")
    Registry.ImportAll()
    Registry.onInstall()
    os.chdir(prev_dir)
    
    Logger.table() \
        .labels(["Test Environment Installed! To run it:"]) \
        .row(["nautica packager test"]).display()
    
        
@packager.command()
def test():
    #project checks
    project_files = os.listdir(".")
    if ".testenv" not in project_files:
        Logger.error("No test environment found. Run 'nautica packager envmake' to create one.")
        return
    
    if "__init__.py" not in project_files:
        Logger.error("No entry point found for your service, make sure __init__.py exists.")
        return
    
    if "project.n3" not in project_files:
        Logger.error("No project.n3 found, are you inside a project?")
        return
        
    #copy service package into plugins
    Config.New("projectdev", ConfigBuilder().build()) #init config
    name = Config("projectdev")["name"]
    
    if not is_valid_name(name) or not name:
        Logger.error(f"Project name contains invalid characters. Allowed: a-z0-9._-")
        return
        
    new_dir = os.path.join(".testenv", "plugins", name)

    def is_ignored(directory, files):
        return [f for f in files if isGitIgnored(os.path.join(directory, f))]

    if os.path.exists(new_dir):
        rmDir(new_dir) #clean previous tests
    
    os.makedirs(new_dir, exist_ok=True)
        
    #copy files
    shutil.copytree(".", new_dir, ignore=is_ignored)
        
    #run it
    from .Run import _run
    _run(".testenv")
    
@packager.command()
def publish():
    #project checks
    project_files = os.listdir(".")
    if "__init__.py" not in project_files:
        Logger.error("No entry point found for your service, make sure __init__.py exists.")
        return
    
    if "project.n3" not in project_files:
        Logger.error("No project.n3 found, are you inside a project?")
        return
    
    #auth
    try:
        user_data = user_data_dir("nautica", ensure_exists=True)
        if ".auth" not in os.listdir(user_data): #no account yet
            Logger.error("You're not logged into your Nautica Package Registry account. Sign in to continue:")
            if not prompt_login():
                return #exit if login unsuccessful
            
        ok, session = login()
        if not ok: #session expired
            Logger.info("You've been signed out of your Nautica Package Registry account. Sign in to continue:")

            if not prompt_login(): return
            _, session = login()
    except Exception as e:
        Logger.trace(e)
        Logger.critical("Failed to authenticate")
        return
    
    #create archive
    files = filterPathsGitIgnore(walkPath("."))
    
    with ZipFile("package.zip", "w") as z:
        for f in files:
            z.write(f)
            
    Logger.ok("Created package archive")

    #upload
    Logger.info("Publishing...")
    
    url = get_reg_url()
    with open("package.zip", "rb") as f:
        r = requests.post(f"{url}/package/publish",
            headers = {"Authorization": session},
            files = {"package": f.read()}
        )
    
    if not r.ok:
        error = getMessage(r.status_code)
        try: error = r.json().get("error", getMessage(r.status_code))
        except: pass
        
        Logger.error(f"Failed to publish package: {error}")
        return
    
    Logger.ok("Package published")

@packager.command()
@click.argument("url", type=str, default="", required=False)
def registry(url: str):
    if not url:
        Logger.info(f"Selected registry: {get_reg_url()}")
        Logger.info("List of available registries:")
        for r in get_all_regs():
            Logger.info(f"* {r}")
    
        return
    
    ok = set_reg_url(url)
    if not ok:
        Logger.error("Failed to change registry")
        return
    
    Logger.ok("Registry changed")