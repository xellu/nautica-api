import time

log_file = f"nautica_{time.strftime("%d_%m_%y__%H_%M_%S", time.localtime())}.log"

NauticaConfigTemplate = {
    "framework": {
        "devMode": True, #set to false for production
        "preloadConfigs": True, #will attempt to load all registered configs at startup
        "disableCacheFiles": False, #will delete __pycache__ and other cache files
        "systemd": False, #if it should run in systemd mode (will disable shell, use remote access)
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
            "enabled": False, #if remote shell access should be enabled
            "accessKeys": [ #access keys for remote shell
                "testkey123" 
            ],
            
            #config for remote access server
            "host": "127.0.0.1",
            "port": 3711
        },
        "sessions": {
            "enabled": False, #whether the session engine will load
        },
        "database": {
            "mongoUri": None #mongodb url to connect to
        }
    }
}

STATUS_CODES = { #https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    103: "Early Hints",
    
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi-Status",
    208: "Already Reported",
    226: "IM Used",
    
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    306: "unused",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Content Too Large",
    414: "URI Too Long",
    415: "Unsupported Media Type",
    416: "Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",
    421: "Misdirected Request",
    422: "Unprocessable Content",
    423: "Locked",
    424: "Failed Dependency",
    425: "Too Early",
    426: "Upgrade Required",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    451: "Unavailable For Legal Reasons",
    
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    506: "Variant Also Negotiates",
    507: "Insufficient Storage",
    508: "Loop Detected",
    510: "Not Extended",
    511: "Network Authentication Required"
}