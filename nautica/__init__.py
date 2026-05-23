_release = "3.0"

import os
from colorama import Fore

def _run():
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
    
    from .manager import Config, ConfigBuilder, Logger

    
    if not os.path.exists("config/nautica.toml"):
        Logger.error("Nautica Project not detected, run 'nautica load' to load an existing project, or 'nautica create <name>' to create a new project")
        return False

    Config.New("nautica",
        ConfigBuilder()
            .add("nautica.debug", True, "Enables tools and endpoints useful of debugging")
            .add("nautica.systemd", False, "Disables the shell service in order to work as a systemd service (Remote Access may be needed)")
            .build()
    )