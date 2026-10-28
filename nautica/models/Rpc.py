class RPCArg:
    def __init__(self, name: str, _type: type):
        self.name = name
        self.type = _type

class RPCFunc:
    def __init__(self, name: str, args: list[RPCArg], kwargs: list[RPCArg]):
        self.name = name
        self.args = args
        self.kwargs = kwargs

class RPCNamespace:
    def __init__(self, name: str):
        self.name = name

        self.funcs: list[RPCFunc] = []