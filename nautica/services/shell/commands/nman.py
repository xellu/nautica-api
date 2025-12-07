from ..descriptor import ShellCommand
from ..shared import logger, ShellBus
from ....ext.utils import hashStr, toRegex

import inspect
import threading
import re

def get_id(x):
    return hashStr(x)[:6]

@ShellBus.on("nm")
@ShellCommand("nman", "A set of tools for debugging. Use 'nman help' for details", "nman <action> [*args]")
def nautica_manager(action=None, *args, **kwargs):
    data = actions.get(action)
    if not data:
        return nm_help()
        
    return data["func"](*args, **kwargs)

def nm_help(action=None):
    if not action:
        logger.info("Available NMan actions:")
        for _, data in actions.items():
            logger.info(f"  {data['usage']} - {data['description']}")
        return
    
    data = actions.get(action.lower())
    if not data:
        return logger.info("NMan action not found")
    
    logger.info(f"About {action.capitalize()}")
    for k, v in data.items():
        logger.info(f"  {k}: {v}")
    

def nm_thread(act="help", target_id=None, *args, **kwargs):
    match act.lower():
        case "list":
            table = logger.table()
            table.labels(["ID", "Name", "Module", "Function"])
            
            for t in threading.enumerate():
                func = t._target.__name__ if t._target is not None else t.ident
                module = t._target.__module__ if t._target is not None else "N/A"
                _id = get_id(f"{t.name}-{module}.{func}")
        
                table.row([_id, t.name, module, func])
                
            table.display()
        
        case "kill":
            if not target_id:
                return logger.error("No thread ID provided")
            
            thread = None
            for t in threading.enumerate():
                func = t._target.__name__ if t._target is not None else t.ident
                module = t._target.__module__ if t._target is not None else "N/A"
                _id = get_id(f"{t.name}-{module}.{func}")
                if _id == target_id:
                    thread = t
                    break
                
            if thread is None:
                return logger.error("Thread not found")
            
            try:
                t.join(timeout=10)
            except Exception as e:
                logger.error(f"Failed to kill thread: {e}")
                logger.trace(e)
            else:
                logger.ok("Thread killed")
        
        case _:
            logger.info("Usage:")
            logger.info("  nman thread list")
            logger.info("  nman thread kill <thread id>")
   
    
def nm_dump(act="help", len_limit=50, *args, **kwargs):
    if len_limit: len_limit = int(len_limit)
    
    match act.lower():
        case "fns":
            import nautica 
            
            table = logger.table()
            table.labels(["Name", "Module", "Args"])
            
            for name, obj in inspect.getmembers(nautica):
                if inspect.isclass(obj):
                    for m_name, m_func in inspect.getmembers(obj, inspect.isfunction):
                        _args = inspect.signature(m_func)
                        _module = m_func.__module__
                        table.row([m_name, _module, _args])
            table.display()
        case "vars":
            import nautica
            
            table = logger.table()
            table.labels(["Name", "Value"])
            
            for name, value in inspect.getmembers(nautica):
                if not (inspect.isfunction(value) or inspect.isclass(value) or inspect.ismodule(value)):
                    table.row([name, str(repr(value))[:len_limit]])
                    
            table.display()
        case _:
            logger.warn("Unknown option")

def nm_http(act="help", *args, **kwargs):
    from ....api.http.router import RouteRegistry
    from .... import Core
    
    service = Core.Runner.servers["http"]

    match act.lower():
        case "info":
            logger.info("HTTP Server Report:")
            logger.info(f"Status: {'ACTIVE' if Core.Config.getMaster("servers.http.enabled") else 'DISABLED'}")
            logger.info(f"Host: {Core.Config.getMaster("servers.http.host")}")
            logger.info(f"Port: {Core.Config.getMaster("servers.http.port")}")
            logger.info(f"Routes: {len(RouteRegistry.routes)}")
                    
            
        case "routes":
            table = logger.table()
            table.labels(["Method", "Route", "Source File"])
            
            for r in RouteRegistry.routes:
                table.row([
                    r["meta"]["method"].upper(),
                    r["route"],
                    r["path"]
                ])
            table.display()
            
        case "reload":
            if len(args) < 1:
                return logger.info("Usage: nman http reload <path>")
            
            pattern = args[0]
            matches = []
            if pattern == "*":
                matches = RouteRegistry.routes[:]
            else:
                regex = toRegex(pattern)
                matches = [r for r in RouteRegistry.routes if regex.match(r["path"])]
            
            if not matches:
                return logger.warn(f"No matches found")
            
            for r in matches:
                service.remove_routes(path=r['path'])
                logger.warn(f"Unloaded {r['path']}")
                
            for r in matches:
                service.preprocess_file(r["path"])
                logger.ok(f"Loaded {r['path']}")
                
            
            
        case _:
            logger.info("Usage:")
            logger.info("  nman http info")
            logger.info("  nman http routes")
            logger.info("  nman http reload <path>")

actions = {
    "help": {
        "func": nm_help,
        "description": "Shows action list or usage guides",
        "usage": "nman help [action]"
    },
    "thread": {
        "func": nm_thread,
        "description": "For listing or killing active threads",
        "usage": "nman thread <list/kill> [*args]"
    },
    "dump": {
        "func": nm_dump,
        "description": "For listing functions and variables",
        "usage": "nman dump <vars/fns> [len limit]"
    },
    "http": {
        "func": nm_http,
        "description": "For insight into the http server",
        "usage": "nman http <info/routes>"
    },
}