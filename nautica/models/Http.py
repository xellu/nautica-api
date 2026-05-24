from starlette.requests import Request
from starlette.datastructures import URL
from .HttpRequirements import Requirement
from ..ext.StatusCodes import getMessage

class RouteRequirements:
    """Declares expected type schemas for each part of an incoming request."""

    def __init__(self, body: dict[type] = None, form: dict[type] = None, headers: dict[type] = None, cookies: dict[type] = None, query: dict[type] = None):
        self.body = body or {}
        self.form = form or {}
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.query = query or {}

    def getBody(self): return self.body
    def getForm(self): return self.form
    def getHeaders(self): return self.headers
    def getCookies(self): return self.cookies
    def getQuery(self): return self.query

    @staticmethod
    def typeToString(v):
        return f"typeOf({v.__name__})" if isinstance(v, type) else str(v)

    def toJson(self):
        """Returns all requirement fields as a JSON-serializable dict, converting types to their name strings."""
        def serialize(d: dict):
            return {k: RouteRequirements.typeToString(v) for k, v in d.items()}

        return {
            "body": serialize(self.body),
            "form": serialize(self.form),
            "headers": serialize(self.headers),
            "cookies": serialize(self.cookies),
            "query": serialize(self.query),
        }


class PreFlightRouteData:
    """Holds route metadata captured at decoration time, before a URL path is assigned."""

    def __init__(self, func, method, name, requirements: RouteRequirements | None = None):
        self.func = func
        self.method = method
        self.name = name
        self.requirements = requirements

    def getFunc(self): return self.func
    def getMethod(self): return self.method
    def getName(self): return self.name
    def getRequirements(self): return self.requirements


class InFlightRouteData:
    """Complete route descriptor built from a PreFlightRouteData and an assigned URL path."""

    def __init__(self, path: str, preflight: PreFlightRouteData, sourceFile: str):
        self.path = path
        self.method = preflight.method
        self.func = preflight.func
        self.requirements = preflight.requirements
        self.sourceFile = sourceFile

    def getFunc(self): return self.func
    def getMethod(self): return self.method
    def getPath(self): return self.path
    def getRequirements(self) -> RouteRequirements | None: return self.requirements
    def getSourceFile(self) -> str: return self.sourceFile


class RequestContext:
    """Wraps a Starlette Request and exposes it to route handlers."""

    def __init__(self, request: Request):
        self.request: Request = request
        self.url: URL = request.url
        self.clientIp: str | None = request.client.host if request and request.client else None

        self.headers: dict = {}
        self.query: dict = {}
        self.cookies: dict = {}
        self.body: dict = {}

class Reply:
    """Builds an HTTP response body; pass kwargs for JSON or positional args for a JSON array."""

    def __init__(self, *array, **json):
        if array and json:
            raise TypeError(f"Mixing positional arguments and keyword arguments is not supported")
        
        self.array = array
        self.json = json    
        self.headers = {
            "Server": "Nautica3"
        }
        self.cookies = {}

    def SetHeader(self, headers: dict):
        """Merges the given dict into the response headers."""
        self.headers = headers

    def SetCookie(self, name: str):
        """Returns a Cookie builder for the given cookie name."""
        return Cookie(name, self)

class ErrorReply:
    def __init__(self, status_code: int, message: str | None = None, details: dict | str | None = None):
        self.status_code = status_code
        self.message = message
        self.details = details
    
    def toReply(self) -> Reply:
        return Reply(
            error = getMessage(self.status_code) if not self.message else self.message,
            details = self.details or {}
        )
    
class Cookie:
    """Fluent builder for a single Set-Cookie header; call .build() to write it onto the Reply."""

    def __init__(self, name: str, reply: Reply):
        self._name = name
        self._reply = reply
        self._value = ""
        self._max_age: int | None = None
        self._path: str = "/"
        self._domain: str | None = None
        self._secure: bool = False
        self._http_only: bool = False
        self._same_site: str | None = None

    def value(self, v: str): return self._set("_value", v)
    def maxAge(self, seconds: int): return self._set("_max_age", seconds)
    def path(self, p: str): return self._set("_path", p)
    def domain(self, d: str): return self._set("_domain", d)
    def secure(self, v: bool = True): return self._set("_secure", v)
    def httpOnly(self, v: bool = True): return self._set("_http_only", v)
    def sameSite(self, v: str): return self._set("_same_site", v)

    def _set(self, attr: str, val):
        setattr(self, attr, val)
        return self

    def build(self):
        """Writes the cookie onto the parent Reply and returns it for further chaining."""
        self._reply.cookies[self._name] = {
            "value": self._value,
            "max_age": self._max_age,
            "path": self._path,
            "domain": self._domain,
            "secure": self._secure,
            "httponly": self._http_only,
            "samesite": self._same_site,
        }
        return self._reply
    
#yes i ai generated the docs, i cba to do this shit