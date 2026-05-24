from ....ext.Util import maybeAwait
from ....ext.StatusCodes import StatusCode
from ....models.Http import PreFlightRouteData, RequestContext, Reply
from ....models.HttpRequirements import RequirementResponse
from ....services import Services
from ....manager import Config, Logger
from .requirements import RequirementParser

from starlette.requests import Request
from starlette.responses import JSONResponse

from functools import wraps
import inspect

class Decorator:
    def __init__(self, manager, method: str, name: str | None):
        self.manager = manager

        self.method = method
        self.name = name

    def decorator(self, func):
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
                    return JSONResponse(content={
                        "error": "Request does not match a defined scheme",
                        "details": args.missingData
                    }, status_code=StatusCode.UNPROCESSABLE_CONTENT)
                ctx.headers = args.headers
                ctx.cookies = args.cookies
                ctx.body = args.body
                ctx.query = args.query
                #---------
            
            if Config("nautica")["http.realIPHeader"]:
                ctx.ip = request.headers.get(Config("nautica")["http.realIPHeader"])

            #run request
            if inspect.signature(func).parameters: result = await maybeAwait(func(ctx))
            else: result = await maybeAwait(func())

            #construct a reply
            if isinstance(result, Reply):
                body = list(result.array) if result.array else result.json
                response = JSONResponse(body)
                for key, val in result.headers.items():
                    response.headers[key] = val
                for name, opts in result.cookies.items():
                    response.set_cookie(name, **opts)
                return response

            return result

        self.manager.temp.append(PreFlightRouteData(
            func = wrapper,
            method = self.method,
            name = self.name if self.name else func.__name__,
            requirements = getattr(func, "_requirements", None)
        ))
        return wrapper