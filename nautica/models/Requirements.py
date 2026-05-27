import re
from starlette.datastructures import UploadFile

class Requirement:
    """Base class for request field validators; subclass and override isValid() to add rules."""

    def __init__(self):
        pass

    def isValid(self, content: dict):
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
            print("doesnt match mime")
            return False
        
        if self.max_size and content.size > self.max_size:
            print("too big")
            return False
        return True
    
    def __str__(self):
        return f"file(size=max({self.maxSizeStr}), mime=anyOf({', '.join(self.mime or [])}))"
    
class RequirementResponse:
    def __init__(self, ok: bool, headers: dict = None, cookies: dict = None, body: dict = None, query: dict = None, files: dict = None, missingData: dict | None = None):
        self.ok = ok
        self.missingData = missingData or {}
        
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.body = body or {}
        self.query = query or {}
        self.files = files or {}