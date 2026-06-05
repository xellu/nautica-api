import tomlkit
import os
from collections.abc import Mapping

from .helper import SubConfig
from ...ext.Path import getRoot
# from .preset import ConfigPresetTOML

ROOT_CONFIGS = {
    "nautica": "config.n3",
    "lock": "package-lock",
}
OPTIONAL_CONFIGS = {
    "projectdev": "project.n3"
}

class ConfigManager:
    def __init__(self):
        from ...manager import Logger as logger

        self.masterCfg = tomlkit.document()
        self.sub_configs = {}

    def __call__(self, configId):
        if configId not in self.sub_configs:
            raise LookupError(f"Unable to find '{configId}' in configs, is it registered?")
        return self.sub_configs[configId]
    
    def Exists(self, configId) -> bool:
        return configId in self.sub_configs
    
    def New(self, configId, template):
        if self.sub_configs.get(configId):
            raise KeyError(f"Config with id '{configId}' is already registered")
        
        from ...manager import Logger as logger

        if configId in ROOT_CONFIGS.keys():
            path = getRoot(ROOT_CONFIGS[configId])
        elif configId in OPTIONAL_CONFIGS.keys():
            path = getRoot(OPTIONAL_CONFIGS[configId])
        else:
            os.makedirs(getRoot("config"), exist_ok=True)
            path = getRoot("config", f"{configId}.toml")
            

        cfg = SubConfig(path=path, template=template)
        self.sub_configs[configId] = cfg

        logger.debug(f"Registered config '{configId}' at '{path}'")
        self.Update(configId, template) #cuh it doesnt update for certain configs
        
    def _merge_missing(self, target, source):
        for key in source:
            raw = source.item(key)
            if key not in target:
                target.add(key, raw)
            elif isinstance(source[key], Mapping) and isinstance(target[key], Mapping):
                self._merge_missing(target[key], source[key])

    def Update(self, configId, update):
        if configId not in self.sub_configs:
            raise LookupError(f"Cannot append to '{configId}': config is not registered")

        cfg = self.sub_configs[configId]
        self._merge_missing(cfg.data, update)
        cfg.save()