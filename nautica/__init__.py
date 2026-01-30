_release = "2.0.0"

from colorama import Fore
print(f"""{Fore.BLUE}                  
      &@@@$                                                                                             
  #@   .@    @=       *****   .***     ****-    ***     **** ************ ****    €&@@$+       ****:    
  %@:  .@   $@&       @@@@@@  :@@@    &@@@@@.   @@@:    %@@@ @@@@@@@@@@@@ @@@@ :@@@@@@@@@@    $@@@@@=   
 @+ %@@-@-@@$ *@      @@@@@@@ :@@@   -@@@-@@@   @@@:    %@@@     @@@@     @@@@ @@@&    %@@@  .@@@ @@@   
      .@@@            @@@ $@@@$@@@   @@@- %@@@  @@@:    %@@@     @@@@     @@@@ @@@           @@@+ $@@@  
 @= %@@:@.@@& €@      @@@   @@@@@@  @@@@@@@@@@% @@@@%-=$%@@@     @@@@     @@@@ @@@@:.  %@@@ @@@@@@@@@@% 
  €@   .@   .@=       @@@    %@@@@ @@@@    $@@@% %@@@@@@@@$      @@@@     @@@@  :@@@@@@@@$ @@@@    $@@@%
  #@   .@    @=                                                                                         
      @@@@@           Nautica v{_release}
{Fore.RESET}""")

from .services.logger import LogManager
from .services.config import ConfigManager
from .services.eventer import EventManager
from .services.shell import ShellService
from .services.database.mongo import MongoDBWrapper
from .runner import Runner

class Core:
   Logger = LogManager("Core")
   Eventer = EventManager()
   Config = ConfigManager()
   Shell = ShellService()
   Runner = Runner()
   
   MongoDB = MongoDBWrapper(Config, Eventer)
   
   
@Core.Eventer.on("ready")
def on_ready():
   Core.Logger.ok("Core initialized")
   
   from .services.eventer import ( builtins )
   
   Core.Shell.import_builtins()
   Core.Runner.start_servers()
   
   Core.MongoDB.start()
   
   
Core.Shell.start()
Core.Eventer.emit("ready")