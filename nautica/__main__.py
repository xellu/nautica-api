from colorama import Fore

try:
    import nautica
except Exception as err:
    import traceback
    from nautica.services.logger import LogManager
    
    logger = LogManager("Nautica.Main")
    logger.trace(err)