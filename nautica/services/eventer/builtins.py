from ..logger import LogManager
from ... import Core, instances
from ...ext.procedures import remove_cache

import os

logger = LogManager("Eventer.BuiltIns")
fallback = {
    "source": "Nautica API",
    "message": "An error occurred in the Nautica API",
}

@Core.Eventer.on("error")
def error_callback(error: Exception, source: str = fallback["source"], message: str = fallback["message"], fatal: bool = False):
    logger.error(f"Error in {source}: {error}")

    if Core.Config.getMaster("framework.devMode"):
        logger.trace(error)

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
    
# Clean shutdown
@Core.Eventer.on("shutdown")
def shutdown(reason: str = None):
    logger.info(f"Shutdown requested ({reason or 'No reason provided'})")
    logger.info("Stopping services. Use 'stop --force' if it is stuck")

    #stop services
    Core.MongoDB.stop()
    
    for db in instances.XelDBInstances:
        db.stop()
        logger.ok(f"Stopped XelDB driver for '{os.path.basename(db.path)}'")

    #additional procedures
    remove_cache()

    logger.ok("Shutdown complete")

    os._exit(0)
    
@Core.Eventer.on("ready")
def on_ready():
    remove_cache()