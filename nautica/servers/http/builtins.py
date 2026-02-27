from . import App
from ... import _release, Core
from ...api.http import Reply, Error, Request as RouteRegistry, Require as RequirementManager
from ...ext.require_util import Require 

from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse
import inspect
import os

@App.route("/favicon.ico")
async def favicon(req: Request):
    if not os.path.exists("src/assets/favicon.ico"):
        return JSONResponse(content=Error("unavailable"), status_code=404)

    # return open("src/assets/favicon.ico", "rb").read()
    return FileResponse("src/assets/favicon.ico")

@App.route("/nautica:about")
async def about_about(req: Request):
    if not Core.Config.getMaster("framework.devMode"): return JSONResponse(content={}, status_code=401)
    
    return JSONResponse(content=Reply(
        server = "Nautica",
        version = _release    
    ))
    
@App.route("/nautica:routes")
async def about_routes(req: Request):
    if not Core.Config.getMaster("framework.devMode"): return JSONResponse(content={}, status_code=401)
    
    service = Core.Runner.servers["http"]
    routes = [f"{r['meta']['method'].upper()} - {r['route']}" for r in service._routes]
    
    return JSONResponse(content=Reply(count=len(routes), routes=routes))
    
@App.route("/nautica:remote_addr")
async def about_remote_addr(req: Request):
    if not Core.Config.getMaster("framework.devMode"): return JSONResponse(content={}, status_code=401)
    
    return JSONResponse(content=Reply(ip=req.scope.get("client")[0]))
    
@App.route("/nautica:require")
async def about_require(req: Request):
    if not Core.Config.getMaster("framework.devMode"): return JSONResponse(content={}, status_code=401)
    
@App.route("/nautica:scheme")
async def about_scheme(req: Request):
    if not Core.Config.getMaster("servers.http.allowSchemeRequests"): return JSONResponse(content={}, status_code=401)
    
    data = await Require(req, uri=str).query()
    if not data.ok: return JSONResponse(Reply(**data.content), 400)
    
    r = RouteRegistry._getFromName(data.content["uri"])
    if not r:
        return JSONResponse(content=Error("Route not found"), status_code=404)
    
    req = RequirementManager._get_requirements(inspect.unwrap(r["route"].func))
    if not req: return JSONResponse(content=Reply()) #no requirements
    
    for field in req.values(): #makes it json serializable (turns classes into strings)
        for key, value in field.items():
            field[key] = value.__name__
    
    return JSONResponse(content=Reply(**req))