class PackageRelease:
    def __init__(self, name, version: str | None = None):
        """
        :name: Package name
        :version: Package version, will default to latest if not provided 
        """
        self.name = name
        self.version = version or "latest"