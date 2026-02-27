from .router import RouteRegistry as Request
from .router import RequestContext as Context
from .require import RequirementManager

def Reply(**kwargs):
    # r = make_response(json.dumps(kwargs))
    # r.headers["Content-Type"] = "application/json"
    
    # return JSONResponse(content=kwargs)
    return kwargs

def ReplyList(*args):
    # r = make_response(json.dumps(args))
    # r.headers["Content-Type"] = "application/json"
    
    # return JSONResponse(content=list(args))
    return args

def Error(message: str, **extras):
    return Reply(error=message, **extras)
    # return JSONResponse(
    #     status_code = code,
    #     content={
    #         "error": message,
    #         **extras
    #     }
    # )

Require = RequirementManager()