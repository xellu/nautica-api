from enum import Enum
from colorama import Fore

class LogLevel(Enum):
    INFO = 1.1
    SUCCESS = 1.2 #had to use floats cause the levelcolors would overwrite for some reason???
    WARN = 2
    ERROR = 3.1
    CRITICAL = 3.2
    
    DEBUG = 5
    TRACE = 3.3
    
    #unusable for calling Logger.log
    ALL = -1
    NONE = 999
    
LevelColors = {
    #level: [tag color, text color]
    LogLevel.INFO: [Fore.BLUE, Fore.RESET],
    LogLevel.SUCCESS: [Fore.LIGHTGREEN_EX, Fore.RESET],
    LogLevel.WARN: [Fore.YELLOW, Fore.RESET],
    LogLevel.ERROR: [Fore.RED, Fore.RESET],
    LogLevel.CRITICAL: [Fore.RED, Fore.LIGHTRED_EX],
    
    LogLevel.DEBUG: [Fore.MAGENTA, Fore.RESET],
    LogLevel.TRACE: [Fore.LIGHTRED_EX, Fore.LIGHTBLACK_EX]
}