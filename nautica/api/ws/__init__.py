from .router import RouteRegistry as Packet

def Serialize(**kwargs):
    return kwargs

def Reply(**kwargs):
    return Serialize(
        ok = True,
        **kwargs
    )

def Error(message, **kwargs):
    return Serialize(
        id = "error",
        ok = False,
        
        error = message,
        **kwargs
    )