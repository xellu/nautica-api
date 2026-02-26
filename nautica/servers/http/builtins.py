from . import App
from ... import _release, Core
from ...api.http import Reply, Error, Request as RouteRegistry, Require as RequirementManager
from ...ext.require_util import Require 

from fastapi import Request
from fastapi.responses import FileResponse
import inspect
import os

@App.route("/favicon.ico")
async def favicon(req: Request):
    if not os.path.exists("src/assets/favicon.ico"):
        return Error("unavailable"), 404

    # return open("src/assets/favicon.ico", "rb").read()
    return FileResponse("src/assets/favicon.ico")

@App.route("/nautica:about")
async def about_about(req: Request):
    if not Core.Config.getMaster("framework.devMode"): return Reply(), 401
    
    return Reply(
        server = "Nautica",
        version = _release    
    )
    
@App.route("/nautica:routes")
async def about_routes(req: Request):
    if not Core.Config.getMaster("framework.devMode"): return Reply(), 401
    
    service = Core.Runner.servers["http"]
    routes = [f"{r['meta']['method'].upper()} - {r['route']}" for r in service._routes]
    
    return Reply(count=len(routes), routes=routes)
    
@App.route("/nautica:remote_addr")
async def about_remote_addr(req: Request):
    if not Core.Config.getMaster("framework.devMode"): return Reply(), 401
    
    return Reply(ip=req.scope.get("client")[0])
    
@App.route("/nautica:require")
async def about_require(req: Request):
    if not Core.Config.getMaster("framework.devMode"): return Reply(), 401
    
@App.route("/nautica:scheme")
async def about_scheme(req: Request):
    if not Core.Config.getMaster("servers.http.allowSchemeRequests"): return Reply(), 401
    
    data = await Require(req, uri=str).query()
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