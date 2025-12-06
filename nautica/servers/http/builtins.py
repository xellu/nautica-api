from . import App
from ...api.http import Reply, Error
from ... import _release, Core

from flask import request
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
    
