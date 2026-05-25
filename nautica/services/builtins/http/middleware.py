from ....ext.Util import maybeAwait
from ....ext.StatusCodes import *
from ....models.Http import PreFlightRouteData, RequestContext, Reply, ErrorReply, InFlightRouteData
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

    @staticmethod
    def handleReply(reply: Reply, status_code: int = 200) -> JSONResponse:
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

    @staticmethod
    def constructResponse(result: any, status_code: int = 200):
        #handle tuples
        if isinstance(result, tuple) and len(result) >= 2:
            obj, status_code = result[0], result[1]
            return Middleware.constructResponse(obj, status_code)
        
        if isinstance(result, Reply):
            return Middleware.handleReply(result, status_code)
        
        if isinstance(result, ErrorReply): #removed, use raise Error() instead
            # return self.handleReply(result.toReply(), result.status_code)
            raise TypeError(f"Unable to serialize ErrorReply. Raise instead of returning an error")
        
        #Handle starlette responses
        if type(result) in [JSONResponse, PlainTextResponse, FileResponse, HTMLResponse, RedirectResponse, StreamingResponse]:
            result.status_code = status_code
            result.headers["Server"] = f"Nautica3"
            return result
        
        #Handle json/dict responses
        if isinstance(result, dict):
            # return JSONResponse(content=result, status_code=status_code)
            return Middleware.handleReply(Reply(**result), status_code)
        if isinstance(result, list):
            return Middleware.handleReply(Reply(*result), status_code)
        
        #Other datatypes as plaintext
        return PlainTextResponse(str(result), status_code=status_code)

    async def run_handler(self, handler, request, ctx) -> any:
        try:
            sig_params = inspect.signature(handler).parameters
            path_kwargs = {k: v for k, v in request.path_params.items() if k in sig_params}
            if sig_params: result = await maybeAwait(handler(ctx, **path_kwargs))
            else: result = await maybeAwait(handler())
            
            return result
        
        except ErrorReply as e:
            return self.handleReply(e.toReply(), e.status_code)
        
        except Exception as e:
            Logger.trace(e)
            return self.handleReply(
                ErrorReply(
                    errorMessage = "Failed to process your request",
                    details = {"exception": str(e)}
                ).toReply(),
                status_code = INTERNAL_SERVER_ERROR
            )

    def decorator(self, func):
        original = inspect.unwrap(func)

        @wraps(func)
        async def wrapper(request: Request):
            #create context
            if not isinstance(request, Request):
                Logger.error(f"Received request as type '{type(request).__name__}', instead of 'starlette.requests.Request', {func=}")
                return self.handleReply(
                    ErrorReply(errorMessage = "Improper request type was passed").toReply(),
                    status_code = INTERNAL_SERVER_ERROR #dont provide error reply with status code directly, it does not handleReply, nor toReply handle that
                )
                
            ctx = RequestContext(request)
            
            route: InFlightRouteData = Services.Get("HTTPRouter").getByFunc(wrapper)
            if not route: Logger.error(f"Route data for function '{wrapper.__name__}' was not found")
            else:
                #process requirements
                args: RequirementResponse = await RequirementParser(route).Extract(request)
                if not args.ok:
                    return self.handleReply(
                        ErrorReply(errorMessage = "Request does not match a defined schema", details=args.missingData).toReply(),
                        status_code = UNPROCESSABLE_CONTENT #dont provide error reply with status code directly, it does not handleReply, nor toReply handle that
                    )
                ctx.headers = args.headers
                ctx.cookies = args.cookies
                ctx.body = args.body
                ctx.query = args.query
                #---------
            
            #get real ip
            if Config("nautica")["http.realIPHeader"]:
                ctx.clientIp = request.headers.get(Config("nautica")["http.realIPHeader"])
    

            #run before request handlers
            for handler in route.getBeforeHandlers():
                result = await self.run_handler(handler, request, ctx)
                if result is not None:
                    return self.constructResponse(result)
    

            #run request
            ctx.response = await self.run_handler(original, request, ctx)
            
            #run after request handlers
            for handler in route.getAfterHandlers():
                self.run_handler(handler, request, ctx)
                
            #construct a reply-----------------
            try:
                return self.constructResponse(ctx.response, 200)
            except Exception as e:
                Logger.trace(e)
                return self.handleReply(
                    ErrorReply(
                        errorMessage  ="Failed to construct a response for your request",
                        details = {"exception": str(e)}
                    ).toReply(),
                    status_code = INTERNAL_SERVER_ERROR
                    # ErrorReply(INTERNAL_SERVER_ERROR, "Failed to construct a response for your request", ).toReply()
                )
                
        self.manager.temp.append(PreFlightRouteData(
            func = wrapper,
            method = self.method,
            name = self.name if self.name else func.__name__,
            
            requirements = getattr(func, "_requirements", None),
        ))
        return wrapper