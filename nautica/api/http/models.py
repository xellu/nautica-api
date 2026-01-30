from flask import Request
import time

class RequestContextArgs:
    def __init__(self, _ok: bool = True, _error: str | None = None, body: dict = None, query: dict = None, cookies: dict = None, headers: dict = None, form: dict = None):
        self._ok = _ok
        self._error = _error
        
        self.body = body if body else {}
        self.query = query if query else {}
        self.cookies = cookies if cookies else {}
        self.headers = headers if headers else {}
        self.form = form if form else {}

    def set(self, field, value):
        if field not in ["body", "query", "cookies", "headers", "form"]: return False
        
        setattr(self, field, value)
        return True
    
    def toDict(self):
        out = {}
        if self.body: out["body"] = self.body
        if self.query: out["query"] = self.query
        if self.cookies: out["cookies"] = self.cookies
        if self.headers: out["headers"] = self.headers
        if self.form: out["form"] = self.form
        
        return out
    
    def __str__(self):
        return f"RequestContextArgs({self.toDict()})"

class RequestContext:
    def __init__(self, request: Request, args: RequestContextArgs, created_at=None):
        self.request = request
        self.args = args
        
        self.created_at = time.time() if not created_at else created_at
        
    def __str__(self): return f"RequestContext({self.args=}, {self.created_at=})"
    

    
class RouteData:
    def __init__(self, method, func, wrapper, name_override = None):
        self.method = method
        self.func = func
        self.wrapper = wrapper
        
        self.name_override = name_override
        