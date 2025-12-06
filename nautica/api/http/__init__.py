import json

from ...servers.http.router import RouteRegistry as Request
from ...servers.http.require import Require
from ... import _release

from flask import request as ctx
from flask import make_response


def Reply(**kwargs):
    r = make_response(json.dumps(kwargs))
    r.headers["Content-Type"] = "application/json"
    
    return r

def Error(message, **kwargs):
    return Reply(error=message, **kwargs)
