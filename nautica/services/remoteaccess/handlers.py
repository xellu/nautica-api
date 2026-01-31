from . import packet_handlers, RemoteAccessHandler, logger
from ...api.ws import Reply, Error

from ... import Core

async def on_auth(client: RemoteAccessHandler, payload: dict):
    key = payload.get("accessKey")
    if not key:
        logger.warn(f"{client.ip} attempted to login to remote access, but didn't provide a key")
        await client.drop("No access key provided")
        return
    
    if key not in Core.Config.getMaster("services.remoteAccess.accessKeys"):
        logger.warn(f"{client.ip} attempted to login to remote access, but provided wrong key")
        await client.drop("Unauthorized")
        return
    
    client.authed = True
    logger.ok(f"{client.ip} logged into remote access")
    return Reply(id="auth")

async def on_command(client: RemoteAccessHandler, payload: dict):
    if not client.authed: return Error("Unauthorized")
    if not payload.get("command"): return Error("No command provided")
    
    Core.Shell.send_command(payload.get("command"))
    return Reply()

packet_handlers["auth"] = on_auth
packet_handlers["command"] = on_command