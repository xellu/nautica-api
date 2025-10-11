import time

log_file = f"nautica_{time.strftime("%d_%m_%y__%H_%M_%S", time.localtime())}.log"

NauticaConfigTemplate = {
    "framework": {
        
    },
    
    "servers": {

        "http": { #config for http server
            "enabled": True,
        
            "host": "0.0.0.0", #127.0.0.1 if local, 0.0.0.0 if public (iirc)
            "port": 8100
        },
        
        "io": { #config for socket.io server
            "enabled": True,
        
            "host": "0.0.0.0",
            "port": 8200
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
            "example": "example.config.json"
        }
    }
}