import re

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
    
class RequirementResponse:
    def __init__(self, ok: bool, headers: dict = None, cookies: dict = None, body: dict = None, query: dict = None, missingData: dict | None = None):
        self.ok = ok
        self.missingData = missingData or {}
        
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.body = body or {}
        self.query = query or {}