from ..logger import LogManager
from ... import Core

import os

logger = LogManager("Nautica.Eventer.BuiltIns")
fallback = {
    "source": "Nautica API",
    "message": "An error occurred in the Nautica API",
}

@Core.Eventer.on("error")
def error_callback(error: Exception, source: str = fallback["source"], message: str = fallback["message"], fatal: bool = False):
    logger.error(f"Error in {source}: {error}")

    # if DEBUG: #TODO: make config work
    #    traceback.print_exc()

    if fatal:
        Core.Eventer.signal("shutdown.crash", f"Fatal error in {source}: {message}")
        
@Core.Eventer.on("shutdown.force")
def force_shutdown(reason: str = None):
    logger.warning(f"Force shutdown requested ({reason or 'no reason provided'})")
    os._exit(0)

@Core.Eventer.on("shutdown.crash")
def crash_shutdown(reason: str = None):
    logger.critical(f"Core crash protocol initiated")
    logger.critical(f"Exit Message: {reason}")
    os._exit(1)
    
#TODO: make a normal shutdown sequence