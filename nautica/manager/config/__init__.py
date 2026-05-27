import tomlkit
import os
from collections.abc import Mapping

from .helper import SubConfig
# from .preset import ConfigPresetTOML

ROOT_CONFIGS = {
    "nautica": "config.n3",
    "package": "package.n3",
}

class ConfigManager:
    def __init__(self):
        from ...manager import Logger as logger

        self.masterCfg = tomlkit.document()
        self.sub_configs = {}

    def getMissingKeys(self, source, template, rel_path: list[str] | None = None):
        rel_path = rel_path if isinstance(rel_path, list) else []
        if not isinstance(source, Mapping):
            return [".".join(rel_path) + " (not a table)"]

        missing = []
        for k, v in template.items():
            cur_path = rel_path.copy() + [k]
            if k not in source:
                missing.append(".".join(cur_path))
            if isinstance(v, Mapping):
                missing += self.getMissingKeys(source.get(k), v, rel_path=cur_path)

        return missing

    def __call__(self, configId):
        if configId not in self.sub_configs:
            raise LookupError(f"Unable to find '{configId}' in configs, is it registered?")
        return self.sub_configs[configId]
    
    def New(self, configId, template):
        if self.sub_configs.get(configId):
            raise KeyError(f"Config with id '{configId}' is already registered")
        
        from ...manager import Logger as logger

        configs_dir = "config"
        os.makedirs(configs_dir, exist_ok=True)
        path = os.path.join(configs_dir, f"{configId}.toml")
        if configId in ROOT_CONFIGS.keys():
            path = ROOT_CONFIGS[configId]

        cfg = SubConfig(path=path, template=template)
        self.sub_configs[configId] = cfg

        logger.ok(f"Registered config '{configId}' at '{path}'")
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