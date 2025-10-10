# Config manager
import json
import os

from ...shared import EventBus, ConfigManInstances
from ..logger import Logger

logger = Logger("Nautica.Services.Config")

class ConfigManager:
    def __init__(self, path, preset = None):
        self.path = path
        
        self.data = {}
        self.preset = preset if preset else {}
        
        self.load() 
        
        ConfigManInstances.append(self)
        
    def load(self):
        try:
            if not os.path.exists(self.path):
                os.makedirs(os.path.basename(self.path), exist_ok=True)
                with open(self.path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(self.template, indent=4))
                    
                Logger.ok(f"Created missing config file at '{self.path}'")
            
            self.data = json.loads(
                open(self.path, "r", encoding="utf-8").read()
            )
        except Exception as e:
            pass
            