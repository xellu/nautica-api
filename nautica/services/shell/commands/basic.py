from ..shared import ShellBus
from ..descriptor import ShellCommand

@ShellCommand("stop", "Stops the server", "stop [--force]")
def shutdown(force=False):
    from .... import Core
    
    Core.Eventer.emit("shutdown" if not force else "shutdown.force")