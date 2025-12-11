from ...ext.static import log_file
from ...instances import LogManInstances
from .levels import LogLevel, LevelColors
from .tableutil import TableUtil

import os
import time
import traceback
from colorama import Fore

class LogManager:
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
            open(self._path, "x", encoding="utf-8").close()
            
        LogManInstances.append(self)
            
    def log(self, message: str, level: LogLevel, *args, **kwargs): 
        if not isinstance(level, LogLevel):
            raise TypeError("Logger level is not an instance of LogLevel")
        
        if level in [LogLevel.ALL, LogLevel.NONE]:
            raise ValueError(f"Log level '{level.name}' is not a valid log level for logging messages")
            
        if level == LogLevel.DEBUG:
            from ... import Core
            if not Core.Config.getMaster("framework.devMode"): return
        
        if not isinstance(message, str): message = str(message)
        
        message = message % args
        for key, value in kwargs.items():
            message.replace("%{key}%", value)
        
        #(HH:MM:SS) [SELF.NAME/LEVEL] message
        timestamp = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime())
        if level.value >= self.level.value:
            color_tag = LevelColors.get(level, [Fore.LIGHTMAGENTA_EX, Fore.LIGHTMAGENTA_EX])[0]
            color_msg = LevelColors.get(level, [Fore.LIGHTMAGENTA_EX, Fore.LIGHTMAGENTA_EX])[1]
            # print(f"{level.name} {LevelColors.get(level)}")
            
            print(f"{Fore.LIGHTBLACK_EX}({timestamp}){Fore.RESET} {color_tag}[{self.name.upper()}/{level.name.upper()}]{Fore.RESET} {color_msg}{message}{Fore.RESET}", **kwargs)
        
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(f"({timestamp}) [{self.name.upper()}/{level.name.upper()}] {message}\n")
            f.flush()
        
    def info(self, message: str, *args, **kwargs):
        if not isinstance(message, str): message = str(message)
        for ln in message.splitlines():
            self.log(ln, LogLevel.INFO, *args, **kwargs)
    
    def warn(self, message: str, *args, **kwargs):
        if not isinstance(message, str): message = str(message)
        for ln in message.splitlines():
            self.log(ln, LogLevel.WARN, *args, **kwargs)
    warning = warn
    
    def error(self, message: str, *args, **kwargs):
        if not isinstance(message, str): message = str(message)
        for ln in message.splitlines():
            self.log(ln, LogLevel.ERROR, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        from ... import Core
        if not Core.Config.getMaster("framework.devMode"): return

        if not isinstance(message, str): message = str(message)        
        for ln in message.splitlines():
            self.log(ln, LogLevel.DEBUG, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        if not isinstance(message, str): message = str(message)
        for ln in message.splitlines():
            self.log(ln, LogLevel.CRITICAL, *args, **kwargs)
    fatal = critical

    def success(self, message: str, *args, **kwargs):
        if not isinstance(message, str): message = str(message)
        for ln in message.splitlines():
            self.log(ln, LogLevel.OK, *args, **kwargs)
    ok = success
        
    def _trace(self, message: str, *args, **kwargs):
        if not isinstance(message, str): message = str(message)
        for ln in message.splitlines():
            self.log(ln, LogLevel.TRACE, *args, **kwargs)
        
    def dir(self, obj: any):
        obj_name = obj.__name__ if hasattr(obj, "__name__") else "obj"
        for key in dir(obj):
            if key in ["__globals__", "__builtins__"]: continue
            
            ln = f"{obj_name}.{key} = {getattr(obj, key)}"
            self.log(ln, LogLevel.DEBUG)
        
    def trace(self, error: Exception):
        trace_str = traceback.format_tb(tb=error.__traceback__)
        trace_data = traceback.extract_tb(error.__traceback__)        

        
        self.error(f"Stacktrace for {type(error).__name__}: {error}")
        
        try:
            file, line, func, content = trace_data[-1]
            self._trace(f"File: {file}")
            self._trace(f"Line: {line}")
            self._trace(f"Func: {func}")
            self._trace(f"Code: {content}")
            
        except:
            self._trace("Unable to extract stacktrace data")
    
        for i, ln in enumerate(trace_str):
            self.error(f"{i+1} ---------------------------")
            self._trace(ln)
            
        self.error("-----------------------------")
        
    def table(self):
        return TableUtil(self)