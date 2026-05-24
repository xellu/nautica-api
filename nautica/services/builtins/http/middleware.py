from ....ext.Util import maybeAwait
from ....ext.StatusCodes import *
from ....models.Http import PreFlightRouteData, RequestContext, Reply, ErrorReply
from ....models.HttpRequirements import RequirementResponse
from ....services import Services
from ....manager import Config, Logger
from .requirements import RequirementParser

from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, FileResponse, HTMLResponse, RedirectResponse, StreamingResponse

from functools import wraps
import inspect

class Middleware:
    def __init__(self, manager, method: str, name: str | None):
        self.manager = manager

        self.method = method
        self.name = name

    def handleReply(self, reply: Reply, status_code: int = 200) -> JSONResponse:
        r = JSONResponse(
            content = list(reply.array) if reply.array else reply.json,
            status_code = status_code
        )
        #set headers
        for key, val in reply.headers.items():
            r.headers[key] = val
        #set cookies
        for name, opts in reply.cookies.items():
            r.set_cookie(name, **opts)
        return r

    def constructResponse(self, result: any, status_code: int = 200):
        if isinstance(result, Reply):
            return self.handleReply(result, status_code)
        
        if isinstance(result, ErrorReply):
            return self.handleReply(ErrorReply.toReply(), result.status_code)
        
        #Handle starlette responses
        if type(result) in [JSONResponse, PlainTextResponse, FileResponse, HTMLResponse, RedirectResponse, StreamingResponse]:
            result.status_code = status_code
            result.headers["Server"] = f"Nautica3"
            return result
        
        #Handle json/dict responses
        if isinstance(result, dict):
            # return JSONResponse(content=result, status_code=status_code)
            return self.handleReply(Reply(**result), status_code)
        if isinstance(result, list):
            return self.handleReply(Reply(*result), status_code)
        
        #Other datatypes as plaintext
        return PlainTextResponse(str(result), status_code=status_code)

    def decorator(self, func):
        original = inspect.unwrap(func)

        @wraps(func)
        async def wrapper(request: Request):
            #create context
            ctx = RequestContext(request)
            
            route = Services.Get("HTTPRouter").getByFunc(wrapper)
            if not route: Logger.error(f"Route data for function '{wrapper.__name__}' was not found")
            else:
                #process requirements
                args: RequirementResponse = await RequirementParser(route).Extract(request)
                if not args.ok:
                    # return JSONResponse(content={
                    #     "error": "Request does not match a defined scheme",
                    #     "details": args.missingData
                    # }, status_code=UNPROCESSABLE_CONTENT)
                    return self.handleReply(
                        ErrorReply(UNPROCESSABLE_CONTENT, "Request does not match a defined schema", details=args.missingData).toReply()
                    )
                ctx.headers = args.headers
                ctx.cookies = args.cookies
                ctx.body = args.body
                ctx.query = args.query
                #---------
            
            #get real ip
            if Config("nautica")["http.realIPHeader"]:
                ctx.clientIp = request.headers.get(Config("nautica")["http.realIPHeader"])

            #run request
            try:
                if inspect.signature(original).parameters: result = await maybeAwait(original(ctx))
                else: result = await maybeAwait(original())
            except Exception as e:
                return self.handleReply(
                    ErrorReply(INTERNAL_SERVER_ERROR, "Failed to process your request", str(e)).toReply()
                )

            #construct a reply-----------------
            
            try:
                #any, status_code format
                if isinstance(result, tuple) and len(result) >= 2:
                    obj, status_code = result[0], result[1]
                    return self.constructResponse(obj, status_code)
                
                #any format
                return self.constructResponse(result, 200)
            except Exception as e:
                Logger.trace(e)
                return self.handleReply(
                    ErrorReply(INTERNAL_SERVER_ERROR, "Failed to construct a response for your request", str(e)).toReply()
                )
            
        self.manager.temp.append(PreFlightRouteData(
            func = wrapper,
            method = self.method,
            name = self.name if self.name else func.__name__,
            requirements = getattr(func, "_requirements", None)
        ))
        return wrapper