import time

log_file = f"nautica_{time.strftime("%d_%m_%y__%H_%M_%S", time.localtime())}.log"

NauticaConfigTemplate = {
    "framework": {
        "devMode": True, #set to false for production
        "preloadConfigs": True, #will attempt to load all registered configs at startup
        "disableCacheFiles": False, #will delete __pycache__ and other cache files
    },
    
    "servers": {

        "http": { #config for http server
            "enabled": True,
        
            "host": "0.0.0.0", #127.0.0.1 if local, 0.0.0.0 if public (iirc)
            "port": 8100,
            
            "realIPHeader": None, #header to get real ip, None - use remote_addr, String - header key (e.g. X-Real-IP, True-Client-IP, CF-Connecting-IP) 
            "allowSchemeRequests": True, #allows requests to /nautica:scheme?uri=<route>
        },

        "ws": { #config for websocket server
            "enabled": True,
            
            "host": "0.0.0.0",
            "port": 8300
        }
    },
    
    "services": {
        "config": {
            # "config_id": "path/to/preset" #config layout/template; path relative to /src/assets
            # "example": "example.config.json"
        },
        "remoteAccess": {
              
        },
        "sessions": {
            "enabled": True, #whether the session engine will load
        },
        "database": {
            "mongoUri": None #mongodb url to connect to
        }
    }
}