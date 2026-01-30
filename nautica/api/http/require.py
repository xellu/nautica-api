import inspect
from functools import wraps

from ...services.logger import LogManager
from ...ext.require_util import Require
from .models import RequestContextArgs

logger = LogManager("API.HTTP.Router")

FIELDS = ["body", "headers", "form", "query", "cookies"]

class RequirementManager:
    def __init__(self):
        """
        Sets minimal request content requirements.
        
        ## Methods:
            - .body(**kwargs)
            - .headers(**kwargs)
            - .query(**kwargs)
            - .form(**kwargs)
            - .cookies(**kwargs)
                    
        ## Example:
            ```
            from nautica.api.http import (Request, Require, Context, Reply)
            
            @Request.GET()
            @Require.body(hello=str)
            def foo(ctx: Context):
                ...
            ```
            \n
            When a request is sent to the endpoint with a body `'{"hello": "world"}'`, it will pass the data into ctx.args. You can retrieve the data like this:
            ```
            ...
            @Require.body(hello=str)
            def foo(ctx: Context):
                hello = ctx.args.body["hello"]
                ...
            ```
            The context will **ALWAYS** contain the required keys.\n
            If a request is missing them or they have a different data type, the request will not go through and it will not reach your function.
     
        """

        
        
        self.map = {}
        
    def _create(self, wrapper, field, kwargs):
        func = inspect.unwrap(wrapper) #unwrap
        if func not in self.map.keys(): self.map[func] = {} #create a requirement registry if not present

        self.map[func][field] = kwargs
        for f in FIELDS:
            if self.map[func].get(f) == None:
                self.map[func][f] = {} #create rest of the fields for them to show up in context.args
        
    def _get_requirements(self, func):
        return self.map.get(func)
    
    def _parse(self, func, request):
        reqs = self._get_requirements(func)
        if not reqs:
            out = RequestContextArgs()
            for field in FIELDS:
                r = Require(request)
                data = getattr(r, "body_soft" if field == "body" else field)()
                out.set(field, data.content)
                
            return out
        
        out = RequestContextArgs()
        for key, value in reqs.items(): #key - field, value - requirements
            r = Require(request, **value)
            if not hasattr(r, key): #if it tries to read from whatever the fuck knows where (very unlikely)
                return RequestContextArgs(_ok=False, _error=f"Unknown field '{key}'")
        
            data = getattr(r, "body_soft" if key == "body" and not value else key)()
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
    
    def headers(self, **kwargs):
        def decorator(func):
            self._create(func, "headers", kwargs)
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
    
    