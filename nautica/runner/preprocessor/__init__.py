from ...services.logger import LogManager
from ...ext.utils import walkPath

from .models import PrepLib

import os


logger = LogManager("Runner.Preprocessor")

class Preprocessor:
    def __init__(self):
        self.libs: list[PrepLib] = []

    def inject_libs(self):
        if not os.path.isdir("src/lib"):
            logger.warning("No libraries injected, 'src/lib' not found")
            return
        
        files = walkPath("src/lib")
        logger.info(f"{files=}")
        