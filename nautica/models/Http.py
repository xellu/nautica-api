from starlette.requests import Request
from starlette.datastructures import URL
from starlette.responses import Response, FileResponse, StreamingResponse, PlainTextResponse, RedirectResponse, HTMLResponse, ContentStream
from starlette.datastructures import UploadFile

from ..ext.StatusCodes import getMessage
from .Requirements import File, Requirement

import time
from os import PathLike

class RouteRequirements:
    """Declares expected type schemas for each part of an incoming request."""

    def __init__(self, body: dict[type] = None, form: dict[type] = None, headers: dict[type] = None, cookies: dict[type] = None, query: dict[type] = None, files: dict[File] = None):
        self.body = body or {}
        self.form = form or {}
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.query = query or {}
        self.files = files or {}

    def getBody(self): return self.body
    def getForm(self): return self.form
    def getHeaders(self): return self.headers
    def getCookies(self): return self.cookies
    def getQuery(self): return self.query
    def getFiles(self): return self.files

    @staticmethod
    def typeToString(v):
        if isinstance(v, dict):
            nested = []
            for k, _type in v.items():
                nested.append(f"{k}={RouteRequirements.typeToString(_type)}")
            return f"nested({', '.join(nested)})"
        
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
            "files": serialize(self.files)
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

    def getBeforeHandlers(self): return getattr(self.func, "_before", [])
    def getAfterHandlers(self): return getattr(self.func, "_after", [])

    def getFunc(self): return self.func
    def getMethod(self): return self.method
    def getPath(self): return self.path
    def getRequirements(self) -> RouteRequirements | None: return self.requirements
    def getSourceFile(self) -> str: return self.sourceFile

class AttachedFile:
    def __init__(self, upload: UploadFile):
        self.file = upload
        self.filename = upload.filename
        self.mime = upload.content_type
        self.size = upload.size #updated on read
    
    async def read(self) -> bytes:
        await self.file.seek(0)

        data = await self.file.read()
        self.size = len(data)
        return data
    
    async def save(self, path: str):
        data = await self.read()
        with open(path, "wb") as f:
            f.write(data)
class RequestContext:
    """Wraps a Starlette Request and exposes it to route handlers."""

    def __init__(self, request: Request):
        self.request: Request = request
        self.url: URL = request.url
        self.clientIp: str | None = request.client.host if hasattr(request, "client") else None
        
        self.headers: dict = {}
        self.query: dict = {}
        self.cookies: dict = {}
        self.body: dict = {}
        self.files: dict[str, AttachedFile] = {}
        
        self.params: dict = request.path_params
        
        self.response: Response | None = None 
        self.created_at = time.time()

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
        self.is_list = False

    def SetHeader(self, headers: dict):
        """Merges the given dict into the response headers."""
        self.headers.update(headers)
        return self

    def SetCookie(self, name: str):
        """Returns a Cookie builder for the given cookie name."""
        return Cookie(name, self)

    def IsList(self, value: bool = True):
        """Tells Middleware to serialize this as a list, if no values are provided"""
        self.is_list = value
        return self
    
    def toJson(self) -> dict | list:
        if self.array or self.is_list:
            return list(self.array)
        return self.json
    
    @staticmethod
    def list(*array):
        return Reply(*array).IsList()
    
    @staticmethod
    def plainText(content: any, media_type: str | None = None) -> PlainTextResponse:
        return PlainTextResponse(content, media_type=media_type)
        
    @staticmethod
    def html(content: any) -> HTMLResponse:
        return HTMLResponse(content)
    
    @staticmethod
    def stream(content: ContentStream, media_type: str | None = None) -> StreamingResponse:
        return StreamingResponse(content, media_type = media_type)
    
    @staticmethod
    def file(path: str | PathLike[str], media_type: str | None = None, filename: str | None = None, method: str | None = None, content_disposition_type: str = "attachment") -> FileResponse:
        return FileResponse(
            path,
            media_type = media_type,
            filename = filename,
            method = method,
            content_disposition_type = content_disposition_type
        )
        
    @staticmethod
    def redirect(url: str | URL) -> RedirectResponse:
        return RedirectResponse(url)

class ErrorReply(Exception):
    """Represents an HTTP error response. Can be returned or raised from a handler."""

    def __init__(self, status_code: int = 400, errorMessage: str | None = None, details: dict | str | None = None):
        """
        Args:
            status_code: HTTP status code to send (default 400).
            errorMessage: Human-readable error message. Falls back to the status code's standard message if omitted.
            details: Extra context attached to the response body; accepts a dict or string.
        """        
        self.status_code = status_code if isinstance(status_code, int) else 400
        self.message = errorMessage
        self.details = details if (isinstance(details, dict) or isinstance(details, str)) else {}

    def SetStatus(self, status_code: int):
        """Set the HTTP status code. Returns self for chaining."""
        self.status_code = status_code
        return self

    def SetError(self, errorMessage: str | None):
        """Override the error message. Returns self for chaining."""
        self.message = errorMessage
        return self

    def SetDetails(self, details: dict | str | None):
        """Attach extra detail to the response body. Returns self for chaining."""
        self.details = details if (isinstance(details, dict) or isinstance(details, str)) else {}
        return self

    def toReply(self) -> Reply:
        """Convert to a Reply suitable for sending as a JSON response body."""
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

class ReplyModel:
    def __init__(self, status_code: int = 200, shape: dict | type | Requirement | ErrorReply = None):
        if not (isinstance(shape, dict) or isinstance(shape, type) or isinstance(shape, Requirement) or isinstance(shape, ErrorReply)):
            raise TypeError(f"ReplyModel only accepts dicts, types, Requirements and ErrorReplies")
    
        self.status_code = status_code
        self.shape = shape
        
#yes i ai generated the docs, i cba to do this shit
