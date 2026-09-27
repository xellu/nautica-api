from ..ext.PackageManager import get_reg_url

import requests

class PackageRelease:
    def __init__(self, name, version: str | None = None):
        """
        :name: Package name
        :version: Package version, will default to "latest" if not provided, use .getVersion() to get actual version
        """
        self.name = name
        self.version = version or "latest"

    def getVersion(self) -> str:
        url = get_reg_url()
        r = requests.get(f"{url}/package/versions?package={self.name}")
        r.raise_for_status()

        return r.json()[-1].get("id")

        # print(r.json())

    def isVersionOf(self, p: PackageRelease):
        return self.name == p.name
