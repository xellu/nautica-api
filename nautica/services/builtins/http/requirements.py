from ....models.Http import InFlightRouteData, RouteRequirements, AttachedFile
from ....models.Requirements import RequirementResponse, Nested, typeToString
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
        self._schema = {}
        
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
    
    def addSchema(self, key: str, schema: dict):
        self._schema[key] = typeToString(schema)

    def toDict(self):
        out = {}
        if self._headers: out["headers"] = self._headers
        if self._cookies: out["cookies"] = self._cookies
        if self._body: out["body"] = self._body
        if self._query: out["query"] = self._query
        if self._form: out["form"] = self._form
        if self._schema: out["schema"] = self._schema
        return out
        
    
class RequirementParser:
    def __init__(self, route: InFlightRouteData):
        self.route = route
        
    async def Extract(self, request: Request) -> RequirementResponse:
        needed = self.route.getRequirements()
        
        if needed is None:
            needed = RouteRequirements()
        
        #get all the bs
        headers = dict(request.headers)
        cookies = request.cookies
        query = dict(request.query_params)
        body = await self.getBody(request)
        files, form = await self.getForm(request)
        
        #and check if it it matches needed data
        
        details = ErrorDetails()
        headersSchema = needed.getHeaders()
        cookiesSchema = needed.getCookies()
        querySchema = needed.getQuery()
        bodySchema = needed.getBody()
        filesSchema = needed.getFiles()

        self._validate(headersSchema, headers, details.addToHeaders, coerce=False)
        self._validate(cookiesSchema, cookies, details.addToCookies, coerce=True)
        self._validate(querySchema, query, details.addToQuery, coerce=True)
        self._validate(bodySchema, body, details.addToBody, coerce=False)
        self._validateFiles(filesSchema, files, details.addToBody)

        if headersSchema: details.addSchema("headers", headersSchema)
        if cookiesSchema: details.addSchema("cookies", cookiesSchema)
        if querySchema: details.addSchema("query", querySchema)
        if bodySchema: details.addSchema("body", bodySchema)
        if filesSchema: details.addSchema("files", filesSchema)

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
    def _validate(schema: Nested, source, add_error, coerce: bool = False):   
        n = Nested(schema)    
        for ok, msg, new_content in n.isValidExt(source, coerce=coerce):
            if not ok: add_error(msg)


    async def getBody(self, request: Request):
        try:
            return await request.json()
        except: return {}

    async def getForm(self, request: Request):
        try:
            form = await request.form();
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

    def _validateFiles(self, schema: dict, files: dict, add_error):
        for k, req in schema.items():
            if k not in files:
                add_error(f"File '{k}' is required but was not provided")
                continue
            
            if not req.isValid(files[k]):
                add_error(f"File '{k}' does not match requirements defined")