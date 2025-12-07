import random
import string
import hashlib
import os
import re
import importlib.util

def randomStr(length: int=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def hashStr(text: str):
    return hashlib.sha256(text.encode()).hexdigest()

def hasUnicode(text: str, allowed: str = "_"):
    for char in text:
        if char not in string.ascii_letters+string.digits + allowed:
            return True
    return False

def walkPath(dir_path: str):
    tree = []
    
    for file in os.listdir(dir_path):
        path = os.path.join(dir_path, file).replace("\\", "/")
        if os.path.isdir(path):
            tree += walkPath(path)
            continue
        
        tree.append(path)
        
    return tree

def importModule(path):
    path = os.path.abspath(path)
    name = os.path.splitext(os.path.basename(path))[0]

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def getExt(fileName):
    if len(fileName.split("."))  <= 1: return ""
    return fileName.split(".")[-1] 

def toRegex(pattern) -> re.Pattern:
    escaped = re.escape(pattern)
    regex = escaped.replace(r"\*", ".*?")
    return re.compile("^" + regex + "$")
