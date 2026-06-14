from ....ext.Util import maybeAwait
from ....ext.StatusCodes import *
from ....models.Http import PreFlightRouteData, RequestContext, Reply, ErrorReply, InFlightRouteData, ReplyModel
from ....models.Requirements import RequirementResponse, typeToString
from ....services import Services
from ....manager import Config, Logger
from .requirements import RequirementParser, Requirement

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
            content = reply.toJson(),
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
        if isinstance(result, (JSONResponse, PlainTextResponse, FileResponse, HTMLResponse, RedirectResponse, StreamingResponse)):
            result.status_code = status_code
            result.headers["Server"] = f"Nautica3"
            return result
        
        #Handle json/dict responses
        if isinstance(result, dict):
            # return JSONResponse(content=result, status_code=status_code)
            return Middleware.handleReply(Reply(**result), status_code)
        if isinstance(result, list):
            return Middleware.handleReply(Reply(*result).asList(), status_code)
        
        #Other datatypes as plaintext
        return PlainTextResponse(str(result), status_code=status_code)

    @staticmethod
    def checkModel(result: any, models: list[ReplyModel] | None) -> tuple[bool, list]:
        if models is None: return True, []
        
        errors = []
        for model in models:
            ok, err = Middleware.isValidShape(result, model)
            if ok:
                return True, []
            errors.append(err)

        return False, errors
        
    @staticmethod
    def isValidShape(result: any, model: ReplyModel, status_code = 200) -> bool:
        shape = model.shape
        
        if isinstance(result, tuple) and len(result) >= 2:
            obj, status_code = result[0], result[1]
            return Middleware.isValidShape(obj, model, status_code)
        
        if status_code != model.status_code:
            return False, f"Response does not match any known model with status code '{model.status_code}'"
        
        if isinstance(shape, ErrorReply):
            if isinstance(result, ErrorReply) and shape.status_code == status_code:
                return True, ""
            return False, f"Expected ErrorReply({model.status_code}), got {type(result).__name__}"

        if isinstance(shape, type):
            if isinstance(result, shape):
                return True, ""
            return False, f"Response model has type of '{shape.__name__}', but '{type(result).__name__}' was provided instead"

        if isinstance(shape, Requirement):
            r = result.toJson() if isinstance(result, Reply) else result
            if shape.isValid(r):
                return True, ""
            return False, f"Response does not match the expression {str(shape)}, {r} was provided instead"

        if isinstance(shape, dict):
            if not isinstance(result, (dict, Reply)):
                return False, f"Response model has type of 'dict', but '{type(result).__name__}' was provided instead"
            
            data = result.toJson() if isinstance(result, Reply) else result
            if isinstance(data, list): return False, f"Response model has type of 'dict', but 'Reply.list' was provided instead"

            errors = []
            for k, v in shape.items():
                if k not in data.keys():
                    errors.append(f"Key '{k}' expected in response model, but is missing")
                    continue
                
                if isinstance(v, Requirement):
                    if not v.isValid(data[k]):
                        errors.append(f"Key '{k}' does not match the expression {str(v)}, type '{type(data[k]).__name__} was provided instead'")
                        continue
                    
                elif not isinstance(v, data[k]):
                    errors.append(f"Key '{k}' does not match the expression {typeToString(v)}, type '{type(data[k]).__name__}' was provided instead")
            
            if errors:
                return False, "; ".join(errors)
            return True, ""

        return False, f"Unknown shape type: {type(shape).__name__}"

    async def run_handler(self, handler, request, ctx) -> any:
        try:
            sig_params = inspect.signature(handler).parameters
            path_kwargs = {k: v for k, v in request.path_params.items() if k in sig_params}
            if sig_params: result = await maybeAwait(handler(ctx, **path_kwargs))
            else: result = await maybeAwait(handler())
            
            return result
        
        except ErrorReply as e:
            raise e
        
        except Exception as e:
            Logger.trace(e)
            raise ErrorReply(INTERNAL_SERVER_ERROR, "Failed to process your request", details={"exception": str(e)})

    def log_response(self, ctx: RequestContext, status_code: int = None):
        status = status_code or ctx.response.status_code
        
        if not Config("nautica")["http.logRequests"] and not isClientError(status) and not isServerError(status):
            return
        
        log_msg = f"{ctx.clientIp}: {ctx.request.method.upper()} -> {ctx.url.path} ({status} {getMessage(status)})"
        if isSuccess(status): Logger.ok(log_msg)
        elif isClientError(status): Logger.warn(log_msg)
        elif isServerError(status): Logger.error(log_msg)
        else: Logger.info(log_msg)

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
            
            route: InFlightRouteData = Services.get("HTTPRouter").getByFunc(wrapper)
            if not route: Logger.error(f"Route data for function '{wrapper.__name__}' was not found")
            else:
                #process requirements
                args: RequirementResponse = await RequirementParser(route).Extract(request)
                if not args.ok:
                    self.log_response(ctx, UNPROCESSABLE_CONTENT)
                    return self.handleReply(
                        ErrorReply(errorMessage = "Request does not match a defined schema", details=args.missingData).toReply(),
                        status_code = UNPROCESSABLE_CONTENT #dont provide error reply with status code directly, it does not handleReply, nor toReply handle that
                    )
                ctx.headers = args.headers
                ctx.cookies = args.cookies
                ctx.body = args.body
                ctx.query = args.query
                ctx.files = args.files
                #---------
            
            #get real ip
            if Config("nautica")["http.realIPHeader"]:
                ctx.clientIp = request.headers.get(Config("nautica")["http.realIPHeader"])
    
            #run before request handlers
            for handler in route.getBeforeHandlers():
                try:
                    result = await self.run_handler(handler, request, ctx)
                    if result is not None:
                        return self.constructResponse(result)
                except ErrorReply as e:
                    self.log_response(ctx, e.status_code)
                    return self.handleReply(e.toReply(), e.status_code)
                
            #run request
            try:
                ctx.response = await self.run_handler(original, request, ctx)
            except ErrorReply as e:
                self.log_response(ctx, e.status_code)
                return self.handleReply(e.toReply(), e.status_code)
            except Exception as e:
                Logger.trace(e)
                self.log_response(ctx, INTERNAL_SERVER_ERROR)
                return self.constructResponse(
                    ErrorReply(
                        errorMessage = "Failed to handle your request",
                        details = {"exception": str(e)}
                    ).toReply(),
                    status_code = INTERNAL_SERVER_ERROR
                    # ErrorReply(INTERNAL_SERVER_ERROR, "Failed to construct a response for your request", ).toReply()
                )
            
            #verify model
            modelOk, modelErrors = self.checkModel(ctx.response, route.getReplyModels())
            isModelStrict = hasattr(original, "_enforceModels")
            
            if not modelOk and isModelStrict:
                return self.constructResponse(
                    ErrorReply(
                        errorMessage = "Response does not match any model",
                        details = {"errors": modelErrors}
                    ).toReply(),
                    status_code = INTERNAL_SERVER_ERROR
                )
            elif not modelOk:
                for err in modelErrors:
                    Logger.error(err)
            
            
            #run after request handlers
            for handler in route.getAfterHandlers():
                await self.run_handler(handler, request, ctx)
            
            #construct
            try:
                ctx.response = self.constructResponse( ctx.response )
            except:
                return self.constructResponse(
                    ErrorReply(
                        errorMessage  = "Failed to construct a response for your request",
                        details = {"exception": str(e)}
                    ).toReply(),
                    status_code = INTERNAL_SERVER_ERROR
                )
            
            #return a constructed reply and log results
            self.log_response(ctx)
            return ctx.response
                
        self.manager.temp.append(PreFlightRouteData(
            func = wrapper,
            method = self.method,
            name = self.name if self.name else func.__name__,
            
            requirements = getattr(func, "_requirements", None),
            replyModel = getattr(func, "_replyModel", None)
        ))
        return wrapper