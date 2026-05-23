from enum import Enum
from colorama import Fore

class LogLevel(Enum):
    DEBUG = 10
    TRACE = 11
    
    INFO = 20
    OK = 21 #alias: OK = success
    WARN = 30
    ERROR = 40
    CRITICAL = 41 #alias: FATAL = critical
    
    SILENT = -999
    
    #unusable for calling Logger.log
    ALL = -1
    NONE = 999
    
LevelColors = {
    #level: [tag color, text color]
    LogLevel.INFO:      [Fore.BLUE,              Fore.RESET],
    LogLevel.OK:        [Fore.LIGHTGREEN_EX,     Fore.RESET],
    LogLevel.WARN:      [Fore.YELLOW,            Fore.RESET],
    LogLevel.ERROR:     [Fore.RED,               Fore.RESET],
    LogLevel.CRITICAL:  [Fore.RED,               Fore.LIGHTRED_EX],
    
    LogLevel.DEBUG:     [Fore.MAGENTA,           Fore.RESET],
    LogLevel.TRACE:     [Fore.LIGHTWHITE_EX,     Fore.LIGHTBLACK_EX]
}