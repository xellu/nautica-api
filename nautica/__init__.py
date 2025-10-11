_release = "2.0.0"

from colorama import Fore
print(f"""{Fore.BLUE}                  
   _  __          __  _         
  / |/ /__ ___ __/ /_(_)______ _
 /    / _ `/ // / __/ / __/ _ `/
/_/|_/\_,_/\_,_/\__/_/\__/\_,_/ 
Running Nautica v{_release}
{Fore.RESET}""")


from .services.logger import LogManager, LogLevel
from .services.config import ConfigManager
from .services.eventer import EventManager

from .ext.static import NauticaConfigTemplate
class Core:
   Logger = LogManager("Nautica.Core")
   Eventer = EventManager()
   Config = ConfigManager()