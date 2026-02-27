import logging
from logging import Logger as DefaultLogger
from ..services.logger import LogManager

class LogData:
    def __init__(self, obj: DefaultLogger, silence=False, rename=None):
        self.obj = obj
        self.silence = silence
        
        self.rename = rename

def PatchLog(log: LogData):
    logger = log.obj

    new_logger = LogManager(logger.name if not log.rename else log.rename)
    if log.silence:
        logger.handlers.clear()
        logger.propagate = False
        logger.disabled = True
        return

    logger.info = new_logger.info
    logger.log = new_logger.info
    logger.debug = new_logger.debug
    logger.warning = new_logger.warning
    logger.error = new_logger.error
    logger.critical = new_logger.critical
    logger.fatal = new_logger.critical
    logger.exception = new_logger.error
    logger.log = new_logger.info