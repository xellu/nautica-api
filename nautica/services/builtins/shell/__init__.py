from ....models.Service import Service
from ....models.Shell import ShellCommand
from ....manager import Config, ConfigBuilder, Logger, LogLevel
from ....services import Services
from ....ext.Util import maybeAwait

from .gui import GUI

import os
import sys
import asyncio
import threading
import pyreadline3

class Shell(Service):
    def __init__(self):
        super().__init__()
        
        self.should_exit = False
        self._loop = None
        
        self.handlers = {
            # "command name": ShellCommand
        }
        
    def onInstall(self):
        Config.Update("nautica",
            ConfigBuilder()
                .add("services.shell", True, comment="Enables command execution and console input")

                .add("shell.systemdMode", False, comment="Disables console input, to work as a systemd service")
                .add("shell.gui", False, comment="Whether to use textual TUI renderer")
                .add("shell.guiTheme", "frost", comment="Available themes are: frost (default), catppuccin, nord, gruvbox, tokyo-night, textual-dark, solarized-light, atom-one-dark, atom-one-light")

                .build()
        )
        
        Config.New("shell-gui",
            ConfigBuilder()
                .add("home.logScroll", True)
                .add("home.threadList", True)
                
                .build()
        )
        
        from .commands import (
            basic
        )

        
    def isEnabled(self):
        return Config("nautica")["services.shell"]
    
    def onStart(self, registry):        
        #import builtin commands
        self.should_exit = False
            
        if Config("nautica")["shell.gui"] and not Config("nautica")["shell.systemdMode"]:
            threading.Thread(target=self._run_gui).start()
        else:
            if Config("nautica")["shell.systemdMode"]: Logger.warn("Shell GUI is not available when running in systemd mode")
            
            #                           dont change ---v
            threading.Thread(target=self._run, daemon=True).start()

    def onClose(self, reason):
        self.should_exit = True
        if GUI.is_running:
            GUI.exit()
    
    def _run(self):
        asyncio.run(self.loop())
    
    def _run_gui(self):
        GUI.run()
        # Services.Reload("Shell")
        Services.onClose("GUI Exited")
    
    @staticmethod
    def parse_command(command: str) -> dict:
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
        
        return out #i pasted this from v2
    
    async def run_parsed_command(self, data: dict) -> tuple[bool, str]:
        for field in ["command", "args", "flags"]: #validate 
            if field not in data.keys(): return False, "Incorrect command data format"
        
        #get handler
        handler: ShellCommand = self.handlers.get(data["command"])
        if not handler:
            return False, "Unknown command"

        #if exists, log the execution (silent to prevent double prints)
        args = " ".join(data['args'])
        flags = " ".join(f"--{k}" for k, v in data['flags'].items())
        Logger.log(f"Running command: {data['command']} {args} {flags}", LogLevel.SILENT)
        
        #validate
        ok, msg = handler.arguments.validate(data["args"], data["flags"])
        if not ok:
            return False, msg

        try:
            res = await maybeAwait(handler.func(*data["args"], **data["flags"]))
        except Exception as e:
            Logger.trace(e)
            return False, f"{e}"
        
        if not res:
            return True, ""
        
        return True, str(res)
    
    async def run_command(self, command: str) -> tuple[bool, str]:
        return await self.run_parsed_command(
            self.parse_command(command)
        )
    
    async def loop(self):
        # Logger.ok("Shell running")
        systemd = Config("nautica")("shell.systemdMode")
        self._loop = asyncio.get_event_loop()
        
        while True:
            try:
                if self.should_exit: break
                
                if systemd:
                    asyncio.sleep(0.25) #prevent from exiting prematurely
                    continue 
                        
                await self.handle_input()        
            
            except (EOFError, SystemExit, KeyboardInterrupt):
                Services.onClose(f"Keyboard Interrupt")
                self.should_exit = True
                break
                
            except Exception as e:
                Logger.trace(e)
        
        if self.should_exit: Logger.ok("Shell service loop exited")
        else: Logger.error("Shell service")
    
    async def handle_input(self):
        c = input()
        if c == ":q":
            Services.onClose()
            
        ok, res = await self.run_command(c)
        if not ok:
            Logger.error(f"Command failed to execute: {res}")
            return

        if res: Logger.ok(res)
        
Shell.Export(Shell)