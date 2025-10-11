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

    # Stop services
    # services = Core.ServiceManager.getAllServices()
    # for service in services:
    #     if service.isRunning():
    #         logger.info(f"Stopping service {service.name}...")
    #         service.stop()
    #         logger.info("All services stopped")

    logger.ok("Shutdown complete")

    os._exit(0)