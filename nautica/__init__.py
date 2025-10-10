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

logger = Logger("Nautica.Core")
logger.info("Initializing core")