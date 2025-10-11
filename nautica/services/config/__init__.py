# Config manager
import json
import os

from ..logger import LogManager
from ...ext.static import NauticaConfigTemplate

logger = LogManager("Nautica.Services.Config")

class ConfigManager:
    def __init__(self):
        self.masterCfg = {}
        
        if "nautica.config.json" not in os.listdir("."):
            logger.warn("Framework configuration file 'nautica.config.json' was not found")
            
            f = open("nautica.config.json", "w", encoding="utf-8")
            f.write(json.dumps(NauticaConfigTemplate, indent=4))
            f.close()
            
            logger.ok("Framework configuration file created")
            
        self.masterCfg = json.loads(
            open("nautica.config.json", "r", encoding="utf-8").read()
        )
        
        if self.getMissingKeys(self.masterCfg, NauticaConfigTemplate):
            raise KeyError(f"Found missing keys in 'nautica.config.json', which are required for framework functionality: {', '.join(self.getMissingKeys(self.masterCfg, NauticaConfigTemplate))}")
            
    def getMissingKeys(self, source: dict, template: dict, rel_path: list[str] | None = None):
        rel_path = rel_path if isinstance(rel_path, list) else [] 
        #^ used to identify what key is missing if nested 
        #e.g.: {"hello": {"world": {"test": "hai"}}} -> if hello.world.test2 is missing it'll show up as 'hello.world.test2' and not test2 (has context)
        if not isinstance(source, dict):
            return [".".join(rel_path) + " (not a dict)"]
        
        missing = []
        
        for k, v in template.items():
            cur_path = rel_path.copy() + [k]
            
            if k not in source.keys():
                missing.append(".".join(cur_path))
            
            if isinstance(v, dict):
                missing += self.getMissingKeys(source.get(k), v, rel_path=cur_path)

        return missing