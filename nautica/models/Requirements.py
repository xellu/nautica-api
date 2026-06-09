import re
from starlette.datastructures import UploadFile

class Requirement:
    """Base class for request field validators; subclass and override isValid() to add rules."""

    def __init__(self):
        pass

    def isValid(self, content: any):
        """Returns True if content satisfies this requirement, False otherwise."""
        pass
    
    def __str__(self):
        return "Expression()"

class AnyOf(Requirement):
    """Validates that content is one of the allowed options."""

    def __init__(self, *options: tuple[any]):
        self.options = list(options)

    def isValid(self, content):
        return content in self.options
    
    def __str__(self):
        return f"anyOf({', '.join(self.options)})"

class AnyTypeOf(Requirement):
    """Validates that the content matches any of the data types provided"""
    def __init__(self, *types: tuple[type]):
        self.types = types
        
    def isValid(self, content):
        ok = False
        for t in self.types:
            if isinstance(content, t): ok = True
        return ok
    
    def __str__(self):
        return f"anyTypeOf({', '.join([t.__name__ for t in self.types])})"

class ExactMatch(Requirement):
    """Validates that content equals the expected value exactly."""

    def __init__(self, match):
        self.match = match

    def isValid(self, content):
        return content == self.match
    
    def __str__(self):
        return f"exactMatch({self.match})"

class RegExMatch(Requirement):
    """Validates that content matches the given regex pattern."""

    def __init__(self, regex: str):
        self._str = regex
        self.regex = re.compile(regex)

    def isValid(self, content) -> bool:
        if not isinstance(content, str): return False
        
        return bool(self.regex.search(str(content)))

    def __str__(self):
        return f"regExMatch({self._str})"
    
class File(Requirement):
    def __init__(self, max_size: int = None, mime: list[str] = None):
        self.max_size = max_size
        self.mime = mime
        
    @staticmethod
    def KB(i: int = 1): return i * 1024
    @staticmethod
    def MB(i: int = 1): return i * 1024 * 1024
    @staticmethod
    def GB(i: int = 1): return i * 1024 * 1024 * 1024
     
    @property
    def maxSizeStr(self) -> str:
        if self.max_size > self.GB():
            return f"{self.max_size / self.GB():.1f}GB"
        elif self.max_size > self.MB():
            return f"{self.max_size / self.MB():.1f}MB"
        elif self.max_size > self.KB():
            return f"{self.max_size / self.KB():.1f}KB"
        return f"{self.max_size}B"
        
    
    def isValid(self, content: UploadFile) -> bool:
        # if not isinstance(content, UploadFile):
        #     print("is not uploadfile")
        #     return False
        
        if self.mime and content.mime not in self.mime:
            # print("doesnt match mime")
            return False
        
        if self.max_size and content.size > self.max_size:
            # print("too big")
            return False
        return True
    
    def __str__(self):
        return f"file(size=max({self.maxSizeStr}), mime=anyOf({', '.join(self.mime or [])}))"
    
class ListOf(Requirement):
    def __init__(self, obj: type | dict | Requirement, min_length: None | int = None, max_length: None | int = None):
        if not (isinstance(obj, type) or isinstance(obj, dict) or isinstance(obj, Requirement)):
            raise TypeError(f"ListOf accepts only types, dicts and Requirements")
        
        
        self.obj = obj
        self.min_length = min_length
        self.max_length = max_length
        
    def isValid(self, content) -> bool:        
        if not isinstance(content, list):
            return False
        
        if self.min_length is not None and len(content) < self.min_length:
            return False
        if self.max_length is not None and len(content) > self.max_length:
            return False
        

        if isinstance(self.obj, type):
            for v in content:
                if not isinstance(v, self.obj): return False
                
        elif isinstance(self.obj, Requirement):
            for v in content:
                if not self.obj.isValid(v): return False
        else:
            for entry in content:
                if not isinstance(entry, dict): return False
                
                if not self._validateDict(entry, self.obj): return False
                
        return True
                
    def _validateDict(self, source: dict, schema: dict): 
        for k, v in schema.items():
            if k not in source.keys(): return False
            
            if isinstance(v, Requirement):
                if not v.isValid(source[k]): return False
                continue
            
            if isinstance(v, dict): 
                if not self._validateDict(source[k], v): return False
                continue
            
            if not isinstance(source[k], v): return False
            
        return True
        
    def __str__(self):
        from .Http import RouteRequirements
        
        return f"listOf({RouteRequirements.typeToString(self.obj)}{', min='+str(self.min_length) if self.min_length else ''}{', max='+str(self.max_length) if self.max_length else ''})"
    
class RequirementResponse:
    def __init__(self, ok: bool, headers: dict = None, cookies: dict = None, body: dict = None, query: dict = None, files: dict = None, missingData: dict | None = None):
        self.ok = ok
        self.missingData = missingData or {}
        
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.body = body or {}
        self.query = query or {}
        self.files = files or {}