from ....models.Http import InFlightRouteData, RouteRequirements, AttachedFile
from ....models.Requirements import RequirementResponse, Requirement, typeToString
from ....manager import Logger, Config
from starlette.requests import Request

class ErrorDetails:
    def __init__(self):
        self.isOk = True
        
        self._headers = []
        self._cookies = []
        self._query = []
        self._body = []
        self._form = []
        
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
        
    def addToForm(self, msg):
        self.isOk = False
        self._form.append(msg)
    
    def toDict(self):
        out = {}
        if self._headers: out["headers"] = self._headers
        if self._cookies: out["cookies"] = self._cookies
        if self._body: out["body"] = self._body
        if self._query: out["query"] = self._query
        if self._form: out["form"] = self._form
        return out
        
    
class RequirementParser:
    def __init__(self, route: InFlightRouteData):
        self.route = route
        
    async def Extract(self, request: Request) -> RequirementResponse:
        needed = self.route.getRequirements()
        
        if needed is None:
            needed = RouteRequirements()
        
        #get all the bs
        headers = request.headers
        cookies = request.cookies
        query = dict(request.query_params)
        body = await self.getBody(request)
        files, form = await self.getForm(request)
        
        #and check if it it matches needed data
        
        details = ErrorDetails()
        include_schema = Config("nautica")["http.includeSchema"]
        
        self._validate(needed.getHeaders(), headers, details.addToHeaders, coerce=False, include_schema=include_schema)
        self._validate(needed.getCookies(), cookies, details.addToCookies, coerce=True, include_schema=include_schema)
        self._validate(needed.getQuery(), query, details.addToQuery, coerce=True, include_schema=include_schema)
        self._validate(needed.getBody(), body, details.addToBody, coerce=False, include_schema=include_schema)
        self._validateFiles(needed.getFiles(), files, details.addToBody, include_schema=include_schema)

        #and return all the shit
        return RequirementResponse(
            ok=details.isOk,
            
            #validated content
            headers = headers,
            cookies = cookies,
            query = query,
            body = body,
            files = files,
            
            missingData=details.toDict() if not details.isOk else None
        ) #wow

    @staticmethod
    def _validate(schema: dict, source, add_error, coerce: bool = False, prefix: str = "", include_schema: bool = True):        
        for k, _type in schema.items():
            if k not in source:
                add_error(f"Key '{k}' is required but was not provided" + (f", schema={typeToString(_type)}" if include_schema else ""))
                continue

            value = source[k]

            #handle requirements
            if isinstance(_type, Requirement):
                if not _type.isValid(value):
                    add_error(f"Key '{prefix}{k}' does not match expression{' '+str(_type) if include_schema else ''}")
            
        
            #nested json
            elif isinstance(_type, dict):
                if not isinstance(source.get(k), dict):
                    add_error(f"Key '{prefix}{k}' does not match expression{' '+typeToString(_type) if include_schema else ''}")
                    continue
                    
                RequirementParser._validate(schema[k], source.get(k), add_error, coerce, prefix=f"{k}.")
                
            #data types
            elif coerce:
                try:
                    if _type is bool:
                        if str(value).lower() not in ("true", "false", "1", "0"):
                            raise ValueError
                    else:
                        _type(value)
                except (ValueError, TypeError):
                    add_error(f"Key '{prefix}{k}' has to match '{typeToString(_type) if include_schema else 'expression'}', got unconvertible value '{value}'")
                else:
                    source[k] = _type(value)
            else:
                if not isinstance(value, _type):
                    add_error(f"Key '{k}' has to match '{typeToString(_type) if include_schema else 'expression'}', got '{type(value).__name__}'")

    async def getBody(self, request: Request):
        try:
            return await request.json()
        except: return {}

    async def getForm(self, request: Request):
        try:
            form = await request.form()
            files = {}
            fields = {}
            for key, value in form.items():
                if hasattr(value, "filename"):  # it's an UploadFile
                    files[key] = AttachedFile(value)
                else:
                    fields[key] = value
            return files, fields
        except Exception as e:
            Logger.trace(e)
            return {}, {}

    def _validateFiles(self, schema: dict, files: dict, add_error, include_schema: bool = True):
        for k, req in schema.items():
            if k not in files:
                add_error(f"File '{k}' is required but was not provided" + (f", schema={str(req)}" if include_schema else ''))
                continue
            
            if not req.isValid(files[k]):
                add_error(f"File '{k}' does not match requirements defined as '{str(req) if include_schema else 'expression'}'")