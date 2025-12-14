from ..services.logger import LogManager
from .utils import walkPath, rmDir
from .. import Core

import os

logger = LogManager("Ext.Procedures")

def remove_cache():
    if not Core.Config.getMaster("framework.disableCacheFiles"): return
    for file in walkPath("src", include_dirs=True):
        if os.path.isdir(file) and file.endswith("__pycache__"):
            rmDir(file)
        
    logger.ok("Cleared cache files")