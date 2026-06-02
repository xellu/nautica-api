import random
import string
import hashlib
import inspect
import os
import re
import sys
import importlib.util
from pathspec import PathSpec
from .Static import GitIgnore
from .Path import getRoot

GitIgnoreSpec = PathSpec.from_lines("gitwildmatch", GitIgnore.splitlines() + [".git/"])


async def maybeAwait(result):
    if inspect.isawaitable(result):
        return await result
    return result

def randomStr(length: int=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def randomHex(length: int=8):
    return "".join(random.choices("0123456789abcdef", k=length))

def hashStr(text: str):
    return hashlib.sha256(text.encode()).hexdigest()

def hasUnicode(text: str, allowed: str = "_"):
    for char in text:
        if char not in string.ascii_letters+string.digits + allowed:
            return True
    return False

def walkPath(dir_path: str, include_dirs=False):
    tree = []

    try:
        entries = os.listdir(dir_path)
    except OSError:
        return tree

    for file in entries:
        path = os.path.join(dir_path, file).replace("\\", "/")
        if os.path.isdir(path):
            tree += walkPath(path, include_dirs)
            if not include_dirs: continue

        tree.append(path)

    return tree

def filterPathsGitIgnore(paths: list[str]) -> list[str]:
    new = []
    for p in paths:
        if not GitIgnoreSpec.match_file(p):
            new.append(p)
            
    return new

def isGitIgnored(path: str) -> bool:
    return GitIgnoreSpec.match_file(path)

def getGitIgnoredPaths(paths: list[str]) -> list[str]:
    new = []
    for p in paths:
        if GitIgnoreSpec.match_file(p):
            new.append(p)
            
    return new

def importModule(path, name: str | None = None):
    path = os.path.abspath(path)
    name = name or os.path.splitext(os.path.basename(path))[0]

    cwd = os.getcwd()
    added = False
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
        added = True

    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if added and cwd in sys.path:
            sys.path.remove(cwd)

def getExt(fileName):
    if len(fileName.split("."))  <= 1: return ""
    return fileName.split(".")[-1] 

def toRegex(pattern) -> re.Pattern:
    escaped = re.escape(pattern)
    regex = escaped.replace(r"\*", ".*?")
    return re.compile("^" + regex + "$")

def rmFile(path) -> tuple[bool, str | None, Exception | None]:
    try:
        os.remove(path)
        return True, None, None
    except Exception as e:
        return False, f"Failed to remove '{path}'", e
        
def rmDir(path) -> tuple[bool, str | None, Exception | None]:
    for file in walkPath(path, include_dirs=True):
        if os.path.isdir(file):
            continue
        ok, msg, err = rmFile(file)
        if not ok:
            return False, msg, err

    for file in sorted(walkPath(path, include_dirs=True), key=len, reverse=True):
        if not os.path.isdir(file):
            continue
        try:
            os.rmdir(file)
        except Exception as e:
            return False, f"Failed to remove directory '{file}'", e

    try:
        os.rmdir(path)
        return True, None, None
    except Exception as e:
        return False, f"Failed to remove directory '{path}'", e