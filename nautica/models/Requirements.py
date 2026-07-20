import re
from typing import Generator
from starlette.datastructures import UploadFile

class Requirement:
    """Base class for request field validators; subclass and override isValid() to add rules."""

    def __init__(self):
        pass

    def isValid(self, content: any):
        """Returns True if content satisfies this requirement, False otherwise."""
        pass
    
    def toComponent(self):
        """Returns a dict representing an OpenAPI Component"""
        return {}
    
    def __str__(self):
        return "Expression()"

class AnyOf(Requirement):
    """Validates that content is one of the allowed options."""

    def __init__(self, *options: tuple[any]):
        self.options = list(options)

    def isValid(self, content):
        for opt in self.options:
            if isinstance(opt, Requirement) and opt.isValid(content): return True
                
        return content in self.options
    
    def toComponent(self):
        if not self.options:
            return { "type": "string", "enum": [] }
            
        return {
            "type": typeToProperName(type(self.options[0])) if len(self.options) > 0 else "string",
            "enum": self.options
        }
    
    def __str__(self):
        return f"anyOf({', '.join(self.options)})"

class AnyTypeOf(Requirement):
    """Validates that the content matches any of the data types provided"""
    def __init__(self, *types: tuple[type | Requirement]):
        self.types = types
        
    def isValid(self, content):
        ok = False
        for t in self.types:
            if isinstance(t, Requirement) and t.isValid(content):
                ok = True
                
            if isinstance(content, t): ok = True
        return ok
    
    def toComponent(self):
        return {
            "anyOf": [{"type": typeToProperName(t)} for t in self.types]
        }
    
    def __str__(self):
        return f"anyTypeOf({', '.join([t.__name__ for t in self.types])})"

class ExactMatch(Requirement):
    """Validates that content equals the expected value exactly."""

    def __init__(self, match):
        self.match = match

    def isValid(self, content):
        return content == self.match
    
    def toComponent(self):
        return {
            "type": typeToProperName(type(self.match)),
            "enum": [self.match]
        }
    
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
    
    def toComponent(self):
        return {
            "type": "string",
            "pattern": self._str
        }

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
        
    def toComponent(self): #don't use in components
        return {
            "requestBody": {
                "content": {
                    "multipart/form-data": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "file": {
                                    "type": "string",
                                    "format": "binary"
                                }
                            }
                        },
                        "encoding": {
                            "file": {
                                "contentType": self.mime
                            }
                        }
                    }
                }
            }
        }
    
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
    
    def toComponent(self):
        d = {
            "type": "array",
            "items": serializeIntoComponent(self.obj)
        }
        if self.min_length: d["minItems"] = self.min_length
        if self.max_length: d["maxItems"] = self.max_length
        
        return d
        
                
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
        return f"{typeToString(self.obj)}[{str(self.min_length)+".." if self.min_length else ('0..' if self.max_length else '')}{str(self.max_length) if self.max_length else ('inf' if self.min_length else '')}]"

class Nested(Requirement):
    def __init__(self, schema: dict[str, type | dict | Requirement]):
        self.schema = schema or {}
   
    def isValidExt(self, content, coerce: bool = False, prefix: str = "") -> Generator[tuple[bool, str | None, dict | None]]: 
        """WILL MUTATE CONTENT IF COERCE IS TRUE"""

        if not isinstance(content, dict):
            yield False, f"Expected a dict, got '{type(content).__name__}'", None
            return

        for k, v in self.schema.items():
            # key not in content
            if k not in content.keys() and not isinstance(v, Optional):
                yield False, f"Key '{prefix}{k}' is required but was not provided", None
                continue

            # invalid requirement
            if isinstance(v, Requirement):
                if not v.isValid(content[k]): yield False, f"Key '{prefix}{k}' does not match expression{' '+str(v) if v else ''}", None
                continue
            
            # nested schema
            if isinstance(v, dict): 
                ok, error, _ = Nested(v).isValidExt(content[k], coerce, f"{prefix}{k}.")
                if not ok: yield False, error, None
                continue

            # regular type
            if not coerce:
                # invalid data type
                if not isinstance(content[k], v):
                    yield False, f"Key '{prefix}{k}' has invalid value", None
                    continue
            else:
                try:
                    if v is bool:
                        if str(content.get(k)).lower() not in ("true", "false", "1", "0"):
                            yield False, f"Key '{prefix}{k}' has to match '{typeToString(v)}', got unconvertible value '{content[k]}'", None
                            continue
                        content[k] = str(content[k]).lower() in ["true", "1"]
                    else:
                        content[k] = v(content[k])
                except (ValueError, TypeError):
                    yield False, f"Key '{prefix}{k}' has to match '{typeToString(v)}', got unconvertible value '{content[k]}'", None
                    continue
                else:
                    content[k] = v(content[k])

        yield True, None, content
    
    def isValid(self, content):
       ok = True
       for k, _, _ in self.isValidExt(content): 
           if not k: ok = False

       return ok

    def __str__(self):
        return typeToString(self.schema)

    def toComponent(self):
        return dictToComponent(self.schema)

class Optional(Requirement):
    def __init__(self, value: type | dict | Requirement):
        self.value = Nested(value) if isinstance(value, dict) else value

    def isValid(self, content):
        print(f"{content=}")
        if not content: return True

        if isinstance(self.value, Requirement):
            return self.value.isValid(content)
        
        return isinstance(content, self.value)

    def toComponent(self):
        if isinstance(self.value, Requirement):
            return self.value.toComponent()
        
        return {"type": typeToProperName(self.value)}
    
    def __str__(self):
        return f"{typeToString(self.value)}?"

#------

class RequirementResponse:
    def __init__(self, ok: bool, headers: dict = None, cookies: dict = None, body: dict = None, query: dict = None, files: dict = None, missingData: dict | None = None):
        self.ok = ok
        self.missingData = missingData or {}
        
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.body = body or {}
        self.query = query or {}
        self.files = files or {}

#helpers-------------

def typeToString(v):
    if isinstance(v, dict):
        nested = []
        for k, _type in v.items():
            nested.append(f"{k}: {typeToString(_type)}")
        return "{" + ', '.join(nested) + "}"
    
    return f"typeOf({v.__name__})" if isinstance(v, type) else str(v)

#openapi bullshi
def typeToProperName(t: type | dict | Requirement):
    if t == Requirement or isinstance(t, Requirement): return "object"
    
    if t == str: return "string"
    if t == int: return "integer"
    if t == float: return "number"
    if t == bool: return "boolean"
    if t == list: return "array"
    if t == dict or isinstance(t, dict): return "object"
    if t == bytes: return "string" #format binary
    if t == None: return "null"
    
    from ..manager import Logger
    Logger.warn(t)
    
    return t.__name__ if hasattr(t, "__name__") else "UNKNOWN" #fallback

def serializeIntoComponent(obj: type | dict | Requirement) -> dict:
    if isinstance(obj, dict):
        return dictToComponent(obj)
    
    if isinstance(obj, Requirement):
        return obj.toComponent()
    
    return {"type": typeToProperName(obj)}

def dictToComponent(d: dict[str, dict | type]) -> dict:
    comp = {
        "type": "object",
        "required": list(d.keys()),
        "properties": {}
    }

    for k, v in d.items():
        if isinstance(v, dict):
            comp["properties"][k] = dictToComponent(v)
        
        elif isinstance(v, Requirement):
            comp["properties"][k] = v.toComponent()
        
        else:
            comp["properties"][k] = {"type": typeToProperName(v)}

    return comp