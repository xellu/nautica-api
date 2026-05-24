from ....models.Http import InFlightRouteData, RouteRequirements
from ....models.HttpRequirements import RequirementResponse, Requirement
from starlette.requests import Request

class ErrorDetails:
    def __init__(self):
        self.isOk = True
        
        self._headers = []
        self._cookies = []
        self._query = []
        self._body = []
        
    def addToHeaders(self, msg):
        self.isOk = False
        self._headers.append(msg)
        
    def addToCookies(self, msg):
        self.isOk = False
        self._cookies.append(msg)
        
    def addToQuery(self, msg):
        self.isOk = False
        self._query.append(msg)
        
    def addToBody(self, msg):
        self.isOk = False
        self._body.append(msg)
    
    def toDict(self):
        out = {}
        if self._headers: out["headers"] = self._headers
        if self._cookies: out["cookies"] = self._cookies
        if self._body: out["body"] = self._body
        if self._query: out["query"] = self._query
        return out
        
    
class RequirementParser:
    def __init__(self, route: InFlightRouteData):
        self.route = route
        
    async def Extract(self, request: Request) -> RequirementResponse:
        needed = self.route.getRequirements()
        
        if needed is None:
            return RequirementResponse(ok=True)
        
        #get all the bs
        headers = request.headers
        cookies = request.cookies
        query = dict(request.query_params)
        body = await self.getBody(request)
        
        #and check if it it matches needed data
        
        details = ErrorDetails()
        
        self._validate(needed.getHeaders(), headers, details.addToHeaders, coerce=False)
        self._validate(needed.getCookies(), cookies, details.addToCookies, coerce=True)
        self._validate(needed.getQuery(), query, details.addToQuery, coerce=True)
        self._validate(needed.getBody(), body, details.addToBody, coerce=False)

        #and return all the shit
        return RequirementResponse(
            ok=details.isOk,
            
            #validated content
            headers = headers,
            cookies = cookies,
            query = query,
            body = body,
            
            missingData=details.toDict() if not details.isOk else None
        ) #wow

    def _validate(self, schema: dict, source, add_error, coerce: bool = False):
        for k, _type in schema.items():
            if k not in source:
                add_error(f"Key '{k}' with is required but was not provided, scheme={RouteRequirements.typeToString(_type)}")
                continue

            value = source[k]

            if isinstance(_type, Requirement):
                if not _type.isValid(value):
                    add_error(f"Key '{k}' does not match expression {str(_type)}")
            elif coerce:
                try:
                    if _type is bool:
                        if str(value).lower() not in ("true", "false", "1", "0"):
                            raise ValueError
                    else:
                        _type(value)
                except (ValueError, TypeError):
                    add_error(f"Key '{k}' has to match '{RouteRequirements.typeToString(_type)}', got unconvertible value '{value}'")
            else:
                if not isinstance(value, _type):
                    add_error(f"Key '{k}' has to match '{RouteRequirements.typeToString(_type)}', got '{type(value).__name__}'")

    async def getBody(self, request: Request):
        try:
            return await request.json()
        except: return {}
