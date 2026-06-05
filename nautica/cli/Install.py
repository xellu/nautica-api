from . import cli

import os
import click

from ..ext.Path import getRoot

from ..manager import Logger, Config, ConfigBuilder
from ..manager.config import ROOT_CONFIGS, SubConfig
from ..models.Package import PackageRelease

from ..services import Registry
from ..ext.PackageUtils import downloadPackage, downloadPackageFromString, removePackage

def installPlugin(package: str | PackageRelease):
    try:
        p = downloadPackageFromString(package) if isinstance(package, str) else downloadPackage(package)
    except Exception as e:
        # Logger.trace(e)
        Logger.critical(f"Package failed to download: {e}")
    else:
        Logger.ok(f"Installed {p.name}, v{p.version}")

@cli.command(aliases=["i"])
@click.argument("packages", nargs=-1, required=False)
def install(packages: list | None = None):
    #install specified packages-----------
    for package in packages or []:
        installPlugin(package)
    
    if packages:
        try:
            Registry.importAll()
            Registry.onInstall()
        except Exception as e:
            Logger.trace(e)
            Logger.critical(f"Packages failed to install: {e}")
        return
    
    #------------------------------------

    #check project files
    Logger.info("Validating project configuration...")    
    for path in ROOT_CONFIGS.values():
        if not os.path.exists(getRoot(path)):
            Logger.error(f"Project config '{path}' is missing!")
            return
    
    #check package versions
    if not Config.Exists("lock"):
        Config.New("lock", ConfigBuilder().build())

    for name, ver in Config("lock").items():
        if not os.path.exists(getRoot("plugins", name, "project.n3")):
            #install plugin
            installPlugin(PackageRelease(name, ver))
            continue
        
        #check version
        cfg = SubConfig(getRoot("plugins", name, "project.n3"), ConfigBuilder().build())
        installedVer = str(cfg.get("version"))
        
        if ver != installedVer:
            Logger.warn(f"Version mismatch for {name}. Lock={ver}, Installed={installedVer}. Re-installing...")
            installPlugin(PackageRelease(name, ver))
    
    #install services
    Logger.info("Installing services...")
    
    Registry.importAll()
    Registry.onInstall()
    
@cli.command()
@click.argument("package", type=str)
def uninstall(package: str):
    try:
        removePackage(package)
    except Exception as e:
        Logger.trace(e)
        return
    
    Logger.ok("Package removed")