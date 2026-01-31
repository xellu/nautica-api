try:
    import nautica
except Exception as err:
    from nautica.services.logger import LogManager
    
    logger = LogManager("Nautica.Main")
    logger.trace(err)