import os
import io
import sys
import requests
import subprocess
from zipfile import ZipFile

from .Path import getRoot
from .Util import rmDir
from .PackageManager import get_reg_url

from ..models.Package import PackageRelease
from ..manager import Config, ConfigBuilder
from ..manager.config.helper import SubConfig

from importlib.metadata import version, PackageNotFoundError
from packaging.requirements import Requirement
from packaging.version import Version


def parsePackageName(package: str) -> PackageRelease:
    if "==" not in package: return PackageRelease(package)
    
    parts = package.split("==")
    if len(parts) == 1: return PackageRelease(package)
    
    return PackageRelease(parts[0], parts[1])

def downloadPackageFromString(package: str) -> PackageRelease:
    return downloadPackage(parsePackageName(package))

def downloadPackage(p: PackageRelease) -> PackageRelease:
    url = get_reg_url() #get repo url
    
    r = requests.get(f"{url}/package/install/{p.name}/{p.version}")
    r.raise_for_status()

    #clear prev plugin data
    path = getRoot("plugins", p.name)
    if os.path.exists(path) or os.path.isdir(path): #delete directory if exists
        ok, _, error = rmDir(path)
        if not ok: raise FileExistsError(f"Failed to update '{p.name}', {error}")

    #unzip new plugin
    os.makedirs(path, exist_ok=True)

    buffer = io.BytesIO(r.content)
    with ZipFile(buffer, "r") as zf:
        zf.extractall(path)
        
    #load project.n3
    project = SubConfig(os.path.join(path, "project.n3"))
    p.version = str(project.get("version"))
    
    
    #install dependencies
    for pipPackage in project.get("pyPackages", []):
        if isPipPackageInstalled(pipPackage): continue
        subprocess.run([sys.executable, "-m", "pip", "install", pipPackage], check=True)
        
    for napiPackage in project.get("dependsOn", []):
        if parsePackageName(napiPackage).name == p.name:
            raise ImportError(f"Package '{p.name}' cannot depend on itself")
            
        downloadPackageFromString(napiPackage)
        
    #save to lock
    if not Config.Exists("lock"): Config.New("lock", ConfigBuilder().build()) #register config
    Config("lock")[p.name] = p.version
    
    return p

def removePackage(package: str) -> bool:
    path = getRoot("plugins", package)
    if not (os.path.exists(path) or os.path.isdir(path)):
        return False
    
    ok, _, err = rmDir(path)
    if not ok: raise err
    
    return True

def isPipPackageInstalled(dep: str) -> bool:
    try:
        req = Requirement(dep)
        installed = Version(version(req.name))
        return not req.specifier or installed in req.specifier
    except PackageNotFoundError:
        return False