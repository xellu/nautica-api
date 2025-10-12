_release = "2.0.0"

from colorama import Fore
print(f"""{Fore.BLUE}                  
   _  __          __  _         
  / |/ /__ ___ __/ /_(_)______ _
 /    / _ `/ // / __/ / __/ _ `/
/_/|_/\\_,_/\\_,_/\\__/_/\\__/\\_,_/
------------------------------------
Running Nautica v{_release}
{Fore.RESET}""")


from .services.logger import LogManager
from .services.config import ConfigManager
from .services.eventer import EventManager
from .services.shell import ShellService

from .services.shell.commands import ( basic, nman )

class Core:
   Logger = LogManager("Nautica.Core")
   Eventer = EventManager()
   Config = ConfigManager()
   Shell = ShellService()
   
@Core.Eventer.on("ready")
def on_ready():
   Core.Logger.ok("Core initialized")
   
   from .services.eventer import ( builtins )
   
Core.Shell.start()
Core.Eventer.emit("ready")