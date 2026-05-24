from ....ext.Util import maybeAwait
from ....models.Http import PreFlightRouteData, RequestContext, Reply

from starlette.requests import Request
from starlette.responses import JSONResponse

import inspect

class Decorator:
    def __init__(self, manager, method: str, name: str | None):
        self.manager = manager

        self.method = method
        self.name = name

    def decorator(self, func):
        async def wrapper(request: Request):
            ctx = RequestContext(request)

            if inspect.signature(func).parameters:
                result = await maybeAwait(func(ctx))
            else:
                result = await maybeAwait(func())

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
            name = self.name or func.__name__,
            requirements = getattr(func, "_requirements", None)
        ))
        return wrapper