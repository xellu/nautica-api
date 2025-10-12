from enum import Enum
from colorama import Fore

class LogLevel(Enum):
    INFO = 10
    SUCCESS = 11 #alias: OK = success
    WARN = 20
    ERROR = 30
    CRITICAL = 31 #alias: FATAL = critical
    
    DEBUG = 40
    TRACE = 50
    SILENT = -999
    
    #unusable for calling Logger.log
    ALL = -1
    NONE = 999
    
LevelColors = {
    #level: [tag color, text color]
    LogLevel.INFO:      [Fore.BLUE,              Fore.RESET],
    LogLevel.SUCCESS:   [Fore.LIGHTGREEN_EX,     Fore.RESET],
    LogLevel.WARN:      [Fore.YELLOW,            Fore.RESET],
    LogLevel.ERROR:     [Fore.RED,               Fore.RESET],
    LogLevel.CRITICAL:  [Fore.RED,               Fore.LIGHTRED_EX],
    
    LogLevel.DEBUG:     [Fore.MAGENTA,           Fore.RESET],
    LogLevel.TRACE:     [Fore.LIGHTWHITE_EX,     Fore.LIGHTBLACK_EX]
}