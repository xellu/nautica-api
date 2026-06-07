from . import cli

import os
import click

from ..ext.Path import getRoot

from ..manager import Logger, Config, ConfigBuilder
from ..manager.config import ROOT_CONFIGS, SubConfig
from ..models.Package import PackageRelease

from ..services import Registry
from ..ext.PackageUtils import downloadPackage, downloadPackageFromString, removePackage

def installPlugin(package: str | PackageRelease, trace = False):
    try:
        p = downloadPackageFromString(package) if isinstance(package, str) else downloadPackage(package)
    except Exception as e:
        if trace: Logger.trace(e)
        Logger.critical(f"Package failed to download: {e}")
    else:
        Logger.ok(f"Installed {p.name}, v{p.version}")

@cli.command(aliases=["i"])
@click.argument("packages", nargs=-1, required=False)
@click.option("--trace", "-t", is_flag=True)
def install(packages: list | None = None, trace: bool = False):
    _install(packages, trace)

def _install(packages: list | None = None, trace: bool = False):
    #install specified packages-----------
    for package in packages or []:
        installPlugin(package, trace)
    
    if packages:
        try:
            Registry.importAll()
            Registry.onInstall()
        except Exception as e:
            if trace: Logger.trace(e)
            else:
                Logger.critical(f"Packages failed to install: {e}")
                Logger.info("For more details run with --trace flag")
            return
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
@click.option("--trace", "-t", is_flag=True)
def uninstall(package: str, trace: bool = False):
    try:
        removePackage(package)
    except Exception as e:
        if trace:
            Logger.trace(e)
            return
        Logger.error(f"Failed to remove package: {e}")
        Logger.info("For more details run with --trace flag")
        return
    
    Logger.ok("Package removed")