from ..ext.PackageManager import get_reg_url

import requests
from packaging.specifiers import SpecifierSet
from packaging.version import Version, InvalidVersion

class PackageRelease:
    def __init__(self, name, version: str | None = None, op: str = "=="):
        """
        :name: Package name
        :version: Package version, will default to "latest" if not provided, use .getVersion() to get actual version
        :op: Version operator (==, >, <, >=, <=), use .resolveVersion() to get an exact matching version
        """
        self.name = name
        self.version = version or "latest"
        self.op = op

    def getVersions(self) -> list[str]:
        url = get_reg_url()
        r = requests.get(f"{url}/package/versions?package={self.name}")
        r.raise_for_status()

        return [v.get("id") for v in r.json()]

    def getVersion(self) -> str:
        return self.getVersions()[-1]

    def specifier(self) -> SpecifierSet:
        if self.version == "latest": return SpecifierSet()
        return SpecifierSet(f"{self.op}{self.version}")

    def resolveVersion(self, spec: SpecifierSet | None = None) -> str:
        """Returns the highest version satisfying spec (defaults to this release's own version and operator)"""
        if spec is None:
            if self.version == "latest": return self.getVersion()
            if self.op == "==": return self.version
            spec = self.specifier()

        if not len(spec): return self.getVersion()

        matching = []
        for v in self.getVersions():
            try:
                if Version(str(v)) in spec: matching.append(str(v))
            except InvalidVersion:
                continue

        if not matching:
            raise ValueError(f"No version of '{self.name}' matches {spec}")

        return max(matching, key=Version)

    def isVersionOf(self, p: PackageRelease):
        return self.name == p.name

    def __str__(self):
        if self.version == "latest": return self.name
        return f"{self.name}{self.op}{self.version}"
