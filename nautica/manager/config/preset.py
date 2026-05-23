ConfigPreset = {
    "framework": {
        "devMode": True, #set to false for production
        "preloadConfigs": True, #will attempt to load all registered configs at startup
        "disableCacheFiles": False, #will delete __pycache__ and other cache files
        "systemd": False, #if it should run in systemd mode (will disable shell, use remote access)
    }
}
