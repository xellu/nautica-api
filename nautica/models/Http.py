from starlette.requests import Request
from starlette.datastructures import URL, ImmutableMultiDict

class RouteRequirements:
    def __init__(self, body: dict = None, form: dict = None, headers: dict = None, cookies: dict = None, query: dict = None):
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


class PreFlightRouteData:
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
    def __init__(self, path, preflight: PreFlightRouteData):
        self.path = path
        self.method = preflight.method
        self.func = preflight.func
        self.requirements = preflight.requirements
        
        
    def getFunc(self): return self.func
    def getMethod(self): return self.method
    def getPath(self): return self.path
    def getRequirements(self) -> RouteRequirements | None: return self.requirements 

class RequestContext:
    def __init__(self, request: Request):
        self.request: Request = request
        self.url: URL = request.url
        
        # self.headers: ImmutableMultiDict = request.headers
        # self.query: ImmutableMultiDict = request.query_params
        # self.cookies: dict = request.cookies
        # self.body = {}

        
    @staticmethod
    def builder(**keys: type):
        return keys
    

class Reply:
    def __init__(self, *array, **json):
        #response body
        self.array = array #still returns in json format, but as a list
        self.json = json
        
        #ext
        self.headers = {}
        self.cookies = {}
        
    def SetHeader(self, headers: dict):
        self.headers = headers
        
    def SetCookie(self, name: str):
        cookie = Cookie(name, self)
        return cookie


class Cookie:
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

    def value(self, v: str):
        self._value = v
        return self

    def maxAge(self, seconds: int):
        self._max_age = seconds
        return self

    def path(self, p: str):
        self._path = p
        return self

    def domain(self, d: str):
        self._domain = d
        return self

    def secure(self, v: bool = True):
        self._secure = v
        return self

    def httpOnly(self, v: bool = True):
        self._http_only = v
        return self

    def sameSite(self, v: str):
        self._same_site = v
        return self

    def build(self):
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