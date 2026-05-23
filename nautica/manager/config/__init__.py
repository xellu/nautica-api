import tomlkit
import os
from collections.abc import Mapping

from .helper import SubConfig
# from .preset import ConfigPresetTOML

# CONFIG_FILE = "nautica.config.toml"

class ConfigManager:
    def __init__(self):
        from ...manager import Logger as logger

        self.masterCfg = tomlkit.document()

        # if CONFIG_FILE not in os.listdir("."):
        #     logger.warn(f"Framework configuration file '{CONFIG_FILE}' was not found")

        #     with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        #         f.write(ConfigPresetTOML)

        #     logger.ok("Framework configuration file created")

        # with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        #     self.masterCfg = tomlkit.load(f)

        self.sub_configs = {}

        # preset = tomlkit.loads(ConfigPresetTOML)
        # missing = self.getMissingKeys(self.masterCfg, preset)
        # if missing:
        #     logger.critical(f"Found {len(missing)} missing keys from '{CONFIG_FILE}'")
        #     for key in missing:
        #         logger.critical(f" - {key}")
        #     raise EnvironmentError(f"Found missing keys in '{CONFIG_FILE}', which are required for framework functionality: {', '.join(missing)}")

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

    # def getMaster(self, key_path, fallback=None):
    #     context = self.masterCfg
    #     parts = key_path.split(".")
    #     for i, key in enumerate(parts):
    #         if not isinstance(context, Mapping):
    #             return fallback
    #         context = context.get(key, {} if i + 1 != len(parts) else fallback)
    #     return context

    # def setMaster(self, key_path, value):
    #     keys = key_path.split(".")
    #     context = self.masterCfg

    #     for i, key in enumerate(keys):
    #         if i < len(keys) - 1:
    #             if key not in context or not isinstance(context[key], Mapping):
    #                 context[key] = tomlkit.table()
    #             context = context[key]
    #         else:
    #             context[key] = value

    #     with open(CONFIG_FILE, "w", encoding="utf-8") as f:
    #         tomlkit.dump(self.masterCfg, f)

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

        cfg = SubConfig(path=path, template=template)
        self.sub_configs[configId] = cfg

        logger.ok(f"Registered config '{configId}' at '{path}'")
        
    def Update(self, configId, update):
        if configId not in self.sub_configs:
            raise LookupError(f"Cannot append to '{configId}': config is not registered")

        cfg = self.sub_configs[configId]

        for key, value in update.items():
            if key not in cfg.data:
                cfg.data.add(key, value)

        cfg.save()