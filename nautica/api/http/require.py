import inspect
from functools import wraps

from ...services.logger import LogManager
from ...ext.require_util import Require
from .models import RequestContextArgs

logger = LogManager("API.HTTP.Router")

class RequirementManager:
    def __init__(self):
        self.map = {}
        
    def _create(self, wrapper, field, kwargs):
        func = inspect.unwrap(wrapper) #unwrap
        if func not in self.map.keys(): self.map[func] = {} #create a requirement registry if not present

        self.map[func][field] = kwargs
        
    def _get_requirements(self, func):
        return self.map.get(func)
    
    def _parse(self, func, request):
        reqs = self._get_requirements(func)
        if not reqs: return RequestContextArgs() #no args -> empty ctx.args
        
        out = RequestContextArgs()
        for key, value in reqs.items(): #key - field, value - requirements
            r = Require(request, **value)
            if not hasattr(r, key): #if it tries to read from whatever the fuck knows where (very unlikely)
                return RequestContextArgs(_ok=False, _error=f"Unknown field '{key}'")
        
            data = getattr(r, key)()
            if not data.ok: #if requirements don't match
                return RequestContextArgs(_ok=False, _error=data.content.get("error", f"Failed to retrieve data for field '{key}'"))
            
            if not out.set(key, data.content):
                logger.warn(f"Failed to set RequestContextArgs attr '{key}' to '{value}'")
                
        return out
            
    def body(self, **kwargs):
        def decorator(func):
            self._create(func, "body", kwargs)
            return func
            
        return decorator
    
    def header(self, **kwargs):
        def decorator(func):
            self._create(func, "header", kwargs)
            return func
            
        return decorator
    
    def form(self, **kwargs):
        def decorator(func):
            self._create(func, "form", kwargs)
            return func
            
        return decorator
    
    def query(self, **kwargs):
        def decorator(func):
            self._create(func, "query", kwargs)
            return func
            
        return decorator
    
    def cookies(self, **kwargs):
        def decorator(func):
            self._create(func, "cookies", kwargs)
            return func
            
        return decorator
    
    