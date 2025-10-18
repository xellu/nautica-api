# Config manager
import json
import os

from ..logger import LogManager
from ...ext.static import NauticaConfigTemplate
from ...instances import ConfigManInstances
from .helper import SubConfig

logger = LogManager("Services.Config")

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
        
        missing = self.getMissingKeys(self.masterCfg, NauticaConfigTemplate)
        if missing:
            logger.critical(f"Found {len(missing)} missing keys from 'nautica.config.json'")
            for key in missing:
                logger.critical(f" - {key}")
                
            raise EnvironmentError(f"Found missing keys in 'nautica.config.json', which are required for framework functionality: {', '.join(missing)}")
        
        ConfigManInstances.append(self)
            
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
    
    def getMaster(self, key_path, fallback=None):
        # {
        #     "framework": {
        #         "devMode": True
        #     }
        # }
        # .getMaster("framework.devMode") -> True
        context = self.masterCfg.copy() 
        for i, key in enumerate(key_path.split(".")):
            if not isinstance(context, dict):
                return fallback
                
            context = context.get(key, {} if i+1 != len(key_path.split('.')) else fallback)
            
        return context
    
    def __call__(self, configId):
        path = self.getMaster(f"services.config.{configId}")
        if not path:
            raise LookupError(f"Unable to find '{configId}' in configs, is it registered?")
        
        template_path = os.path.join("src", "assets", path)
        template = {}
        
        template = json.loads(
            open(template_path, "r", encoding="utf-8").read()
        )
        
        return SubConfig(
            path = path,
            template = template
        )
        