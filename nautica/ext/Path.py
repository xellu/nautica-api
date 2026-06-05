import os

_root = "."

def setRoot(path: str):
    global _root
    _root = os.path.abspath(path)
    
def getRoot(*parts):
    return os.path.join(_root, *parts)