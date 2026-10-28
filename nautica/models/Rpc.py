class RPCArg:
    def __init__(self, name: str, _type: type, default = None):
        self.name = name
        self.type = _type
        self.default = default

    def __str__(self):
        return f"{self.name}: {self.type.__name__}{' = '+str(self.default) if not (self.default is None) else ''}"

class RPCFunc:
    def __init__(self, func: callable, name: str, args: list[RPCArg], kwargs: list[RPCArg], type_hint: type):
        self.func = func
        self.name = name
        self.type_hint = type_hint

        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return f"{self.name}(args=[{', '.join([str(a) for a in self.args])}], kwargs={'{'+', '.join([str(a) for a in self.kwargs])+'}'})->{self.type_hint}"

class RPCNamespace:
    def __init__(self, name: str):
        self.name = name

        self.funcs: list[RPCFunc] = []

    def addFunction(self, fn: RPCFunc):
        if not isinstance(fn, RPCFunc): raise ValueError(f"Provided function '{fn}' is of type '{type(fn).__name__}', expected 'RPCFunc'")

        for f in self.funcs:
            if f.name == fn.name: raise NameError(f"Function with the same name ({fn.name}) is already registered in this namespace")

        self.funcs.append(fn)

    def __str__(self):
        return f"{self.name}(funcs=[{', '.join(str(f) for f in self.funcs)}])"