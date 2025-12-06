class _RouteRegistry:
    def __init__(self):
        self.routes = []
        
    def _create(self, method, func, name_override = None):
        self.routes.append({
            "method": method,
            "func": func,
            "name_override": name_override
        })
        
    def GET(self, name_override: str | None = None):
        def decorator(func):
            self._create("get", func, name_override)
            return func
        return decorator

    def POST(self, name_override: str | None = None):
        def decorator(func):
            self._create("post", func, name_override)
            return func
        return decorator

    def HEAD(self, name_override: str | None = None):
        def decorator(func):
            self._create("head", func, name_override)
            return func
        return decorator

    def PUT(self, name_override: str | None = None):
        def decorator(func):
            self._create("put", func, name_override)
            return func
        return decorator
    
    def DELETE(self, name_override: str | None = None):
        def decorator(func):
            self._create("delete", func, name_override)
            return func
        return decorator

    def CONNECT(self, name_override: str | None = None):
        def decorator(func):
            self._create("connect", func, name_override)
            return func
        return decorator

    def OPTIONS(self, name_override: str | None = None):
        def decorator(func):
            self._create("options", func, name_override)
            return func
        return decorator

    def TRACE(self, name_override: str | None = None):
        def decorator(func):
            self._create("trace", func, name_override)
            return func
        return decorator
    
    def PATCH(self, name_override: str | None = None):
        def decorator(func):
            self._create("patch", func, name_override)
            return func
        return decorator

    

    

    