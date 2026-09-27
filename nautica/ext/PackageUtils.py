import os
import io
import re
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
from packaging.specifiers import SpecifierSet
from packaging.version import Version, InvalidVersion


PACKAGE_SPEC = re.compile(r"^\s*([^<>=\s]+)\s*(==|>=|<=|>|<)\s*(\S+)\s*$")

def parsePackageName(package: str) -> PackageRelease:
    match = PACKAGE_SPEC.match(package)
    if not match: return PackageRelease(package.strip())

    name, op, ver = match.groups()
    return PackageRelease(name, ver, op)

class InstallSession:
    """Tracks version constraints across a single install run, so shared dependencies resolve to one compatible version"""
    def __init__(self):
        self.constraints: dict[str, list[tuple[str, str]]] = {} #name -> [(requiredBy, specifier)]
        self.installed: dict[str, str] = {} #installed during this session
        self.existing: dict[str, str] = {} #installed before this session
        self.inProgress: set[str] = set()

    def seed(self):
        """Loads constraints from already installed plugins"""
        plugins = getRoot("plugins")
        if not os.path.isdir(plugins): return self

        for name in os.listdir(plugins):
            path = os.path.join(plugins, name, "project.n3")
            if not os.path.exists(path): continue

            project = SubConfig(path)
            self.existing[name] = str(project.get("version"))
            for dep in project.get("dependsOn", []):
                dep = parsePackageName(dep)
                self.addConstraint(dep.name, name, str(dep.specifier()))

        return self

    def addConstraint(self, name: str, requiredBy: str, spec: str):
        self.constraints.setdefault(name, []).append((requiredBy, spec))

    def dropConstraintsFrom(self, requiredBy: str):
        for name in self.constraints:
            self.constraints[name] = [c for c in self.constraints[name] if c[0] != requiredBy]

    def spec(self, name: str) -> SpecifierSet:
        spec = SpecifierSet()
        for _, s in self.constraints.get(name, []):
            spec &= SpecifierSet(s)
        return spec

    def satisfies(self, name: str, ver: str) -> bool:
        try: return Version(ver) in self.spec(name)
        except InvalidVersion: return False

    def conflictMessage(self, name: str) -> str:
        reqs = ", ".join(f"{by} requires {s or 'any version'}" for by, s in self.constraints.get(name, []))
        return f"Conflict for '{name}': {reqs}"

def downloadPackageFromString(package: str, session: InstallSession | None = None, requiredBy: str = "project") -> PackageRelease:
    return downloadPackage(parsePackageName(package), session, requiredBy)

def downloadPackage(p: PackageRelease, session: InstallSession | None = None, requiredBy: str = "project") -> PackageRelease:
    if session is None: session = InstallSession().seed()
    url = get_reg_url() #get repo url

    #check against constraints from other packages
    session.addConstraint(p.name, requiredBy, str(p.specifier()))
    spec = session.spec(p.name)

    if p.name in session.installed and session.satisfies(p.name, session.installed[p.name]):
        return PackageRelease(p.name, session.installed[p.name])
    if requiredBy != "project" and p.name in session.existing and session.satisfies(p.name, session.existing[p.name]):
        return PackageRelease(p.name, session.existing[p.name])
    if p.name in session.inProgress:
        raise ImportError(session.conflictMessage(p.name))

    #resolve version specifier to an exact version
    try:
        p.version = p.resolveVersion(spec)
    except ValueError:
        raise ImportError(session.conflictMessage(p.name))
    p.op = "=="

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
    session.installed[p.name] = p.version
    session.dropConstraintsFrom(p.name) #old version's constraints no longer apply


    #install dependencies
    for pipPackage in project.get("pyPackages", []):
        if isPipPackageInstalled(pipPackage): continue
        subprocess.run([sys.executable, "-m", "pip", "install", pipPackage], check=True)

    session.inProgress.add(p.name)
    try:
        for napiPackage in project.get("dependsOn", []):
            if parsePackageName(napiPackage).name == p.name:
                raise ImportError(f"Package '{p.name}' cannot depend on itself")

            downloadPackageFromString(napiPackage, session, p.name)
    finally:
        session.inProgress.discard(p.name)

    #save to lock
    if not Config.Exists("lock"): Config.New("lock", ConfigBuilder().build()) #register config
    Config("lock")[p.name] = p.version
    
    return p

def removePackage(package: str) -> bool:
    path = getRoot("plugins", package)
    if not (os.path.exists(path) or os.path.isdir(path)):
        raise FileNotFoundError("Package not installed")
    
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