from . import App
from ... import _release, Core
from ...api.http import Reply, Error, Request as RouteRegistry, Require as RequirementManager
from ...ext.require_util import Require 

from flask import request
import inspect
import os

@App.route("/favicon.ico")
def favicon():
    if not os.path.exists("src/assets/favicon.ico"):
        return Error("unavailable"), 404

    return open("src/assets/favicon.ico", "rb").read()

@App.route("/nautica:about")
def about_about():
    if not Core.Config.getMaster("framework.devMode"): return Reply(), 401
    
    return Reply(
        server = "Nautica",
        version = _release    
    )
    
@App.route("/nautica:routes")
def about_routes():
    if not Core.Config.getMaster("framework.devMode"): return Reply(), 401
    
    service = Core.Runner.servers["http"]
    routes = [f"{r['meta']['method'].upper()} - {r['route']}" for r in service._routes]
    
    return Reply(count=len(routes), routes=routes)
    
@App.route("/nautica:remote_addr")
def about_remote_addr():
    if not Core.Config.getMaster("framework.devMode"): return Reply(), 401
    
    return Reply(ip=request.remote_addr)
    
@App.route("/nautica:scheme")
def about_scheme():
    if not Core.Config.getMaster("servers.http.allowSchemeRequests"): return Reply(), 401
    
    data = Require(request, uri=str).query()
    if not data.ok: return Reply(**data.content), 400
    
    r = RouteRegistry._getFromName(data.content["uri"])
    if not r:
        return Error("Route not found"), 404
    
    req = RequirementManager._get_requirements(inspect.unwrap(r["route"].wrapper))
    if not req: return Reply() #no requirements
    
    for field in req.values(): #makes it json serializable (turns classes into strings)
        for key, value in field.items():
            field[key] = value.__name__
    
    return Reply(**req)