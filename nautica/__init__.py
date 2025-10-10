_release = "2.0.0"

from colorama import Fore
print(f"""{Fore.BLUE}                  
   _  __          __  _         
  / |/ /__ ___ __/ /_(_)______ _
 /    / _ `/ // / __/ / __/ _ `/
/_/|_/\_,_/\_,_/\__/_/\__/\_,_/ 
Running Nautica v{_release}
{Fore.RESET}""")


from .services.logger import Logger, LogLevel
from .services.config import ConfigManager

logger = Logger("Nautica.Core")
logger.info("Logging manager initialized")

Config = ConfigManager("nautica.config.json")