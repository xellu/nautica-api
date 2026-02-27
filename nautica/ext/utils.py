import random
import string
import hashlib
import inspect
import os
import re
import importlib.util

from ..services.logger import LogManager

logger = LogManager("Ext.Utils")


async def maybeAwait(result):
    if inspect.isawaitable(result):
        return await result
    return result

def randomStr(length: int=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def hashStr(text: str):
    return hashlib.sha256(text.encode()).hexdigest()

def hasUnicode(text: str, allowed: str = "_"):
    for char in text:
        if char not in string.ascii_letters+string.digits + allowed:
            return True
    return False

def walkPath(dir_path: str, include_dirs=False):
    tree = []
    
    for file in os.listdir(dir_path):
        path = os.path.join(dir_path, file).replace("\\", "/")
        if os.path.isdir(path):
            tree += walkPath(path, include_dirs)
            if not include_dirs: continue
        
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

def rmFile(path):
    try:
        os.remove(path)
    except Exception as e:
        logger.error(f"Failed to remove '{path}'")
        logger.trace(e)
        
def rmDir(path):
    for file in walkPath(path, include_dirs=True):
        if os.path.isdir(file):
            try:
                os.rmdir(file)
            except Exception as e:
                logger.error(f"Failed to remove directory '{file}'")
                logger.trace(e)
            continue
        
        rmFile(file)
    os.rmdir(path)