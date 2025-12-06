import json

from ...servers.http.router import RouteRegistry as Request
from ...servers.http.requirements import RequirementRegistry as Require
from ...servers.http.router import RequestContext as Context
from ... import _release

from flask import make_response

def Reply(**kwargs):
    r = make_response(json.dumps(kwargs))
    r.headers["Content-Type"] = "application/json"
    
    return r

def Error(message, **kwargs):
    return Reply(error=message, **kwargs)
