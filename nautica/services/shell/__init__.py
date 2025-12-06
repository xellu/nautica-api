import threading
import time

from ..logger.levels import LogLevel
from .shared import logger, ShellBus

class ShellService:
    def __init__(self):
        self.handlers = {}
        self.lock = threading.Lock()
        
        self.thread = None
        self.running = False
        
    def import_builtins(self): #<--------- REGISTER COMMANDS HERE
        from .commands import (
            basic,
            nman
        )
        
    def register_command(self, func, name, description, usage):
        self.handlers[name] = {
            "func": func,
            "description": description,
            "usage": usage
        }
        
        logger.debug(f"Registered command '{name}', {func=}")
        return func

    @ShellBus.on("respond")
    def on_respond(self, command: str, message: str):
        logger.info(f"{command} -> {message}")

    def run_command(self, data: dict):
        args = " ".join(data['args'])
        flags = " ".join(f"--{k}" for k, v in data['flags'].items())
        
        logger.log(f"Running command: {data['command']} {args} {flags}", LogLevel.SILENT)
        return ShellBus.signal(data["command"], *data["args"], **data["flags"])

    def parse_data(self, command: str):
        #format: command arg --flag
        data = command.split(" ")
        out = {
            "command": data[0],
            "args": [],
            "flags": {}
        }

        for i in range(1, len(data)):
            if data[i].startswith("--"):
                out["flags"][data[i][2:]] = True
            else:
                out["args"].append(data[i])
        
        return out


    def loop(self):
        logger.ok("Shell Service started")
        while self.running:
            try:
                command = input("")
                if command.strip() == "":
                    continue
                
                data = self.parse_data(command)
                response = self.run_command(data)
                if response == False:
                    logger.warn(f"Command '{data['command']}' was not found")
            
            except KeyboardInterrupt as err:
                from ... import Core
                Core.Eventer.emit("shutdown", "Requested by Admin")
            
            except Exception as err:
                from ... import Core
                if isinstance(err, KeyboardInterrupt) or isinstance(err, SystemExit) or str(err) == "":
                    Core.Eventer.emit("shutdown", "Requested by admin")
                    return
                logger.error(f"Error in shell loop: {err}")

        logger.warn("Shell loop exited")
        self.stop()

        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logger.ok("Shell Service stopped")