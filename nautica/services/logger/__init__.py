from ...ext.static import log_file
from .levels import LogLevel, LevelColors

import os
import time
from colorama import Fore

class Logger:
    def __init__(self, name: str, level: LogLevel = LogLevel.ALL):
        """
        Nautica's Logging Manager
        
        Args:
            name (str): Tag name for the logger instance
            level (LogLevel/int): A minimal level required for a message to get printed
        """
        
        self.name: str = name
        self.level: LogLevel = level
        self._path = os.path.join(".logs", log_file)
        
        # create logs dir if not exists
        if ".logs" not in os.listdir():
            os.makedirs(".logs", exist_ok = True)
        
        # create log file if not exists
        if not os.path.exists(self._path):
            open(self._path, "x").close()
            
    def log(self, message: str, level: LogLevel, *args, **kwargs): 
        if not isinstance(level, LogLevel):
            raise TypeError("Logger level is not an instance of LogLevel")
        
        if level in [LogLevel.ALL, LogLevel.NONE]:
            raise ValueError(f"Log level '{level.name}' is not a valid log level for logging messages")
            
        message = message % args
        for key, value in kwargs.items():
            message.replace("%{key}%", value)
        
        #(HH:MM:SS) [SELF.NAME/LEVEL] message
        if level.value >= self.level.value:
            color_tag = LevelColors.get(level, [Fore.LIGHTMAGENTA_EX, Fore.LIGHTMAGENTA_EX])[0]
            color_msg = LevelColors.get(level, [Fore.LIGHTMAGENTA_EX, Fore.LIGHTMAGENTA_EX])[1]
            # print(f"{level.name} {LevelColors.get(level)}")
            
            print(f"{Fore.LIGHTBLACK_EX}({time.strftime('%H:%M:%S', time.localtime())}){Fore.RESET} {color_tag}[{self.name.upper()}/{level.name.upper()}]{Fore.RESET} {color_msg}{message}{Fore.RESET}", **kwargs)
        
        with open(self._path, "a") as f:
            f.write(f"({time.strftime('%H:%M:%S', time.localtime())}) [{self.name.upper()}/{level.name.upper()}] {message}\n")
            f.flush()
        
    def info(self, message: str, *args, **kwargs):
        self.log(message, LogLevel.INFO, *args, **kwargs)
    
    def warn(self, message: str, *args, **kwargs):
        self.log(message, LogLevel.WARN, *args, **kwargs)
    warning = warn
    
    def error(self, message: str, *args, **kwargs):
        self.log(message, LogLevel.ERROR, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        self.log(message, LogLevel.DEBUG, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        self.log(message, LogLevel.CRITICAL, *args, **kwargs)
    fatal = critical

    def trace(self, message: str, *args, **kwargs):
        self.log(message, LogLevel.TRACE, *args, **kwargs)

    def success(self, message: str, *args, **kwargs):
        self.log(message, LogLevel.SUCCESS, *args, **kwargs)
    ok = success
    
    