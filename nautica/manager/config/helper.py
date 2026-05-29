import tomlkit
from collections.abc import Mapping

class SubConfig:
    def __init__(self, path: str, template: Mapping | None = None, max_retries: int = 3):
        self.fault_retry_threshold = max_retries
        self.fault_retry_count = 0

        self.path = path
        self.template = template

        self.data = tomlkit.document()
        self.load()

    def load(self):
        from ...manager import Logger as logger

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = tomlkit.load(f)

        except Exception:
            self.fault_retry_count += 1

            if self.fault_retry_count >= self.fault_retry_threshold:
                logger.error("Unable to load configuration file, automatic overwrite aborted (max retries exceeded)")
                return

            if self.fault_retry_count > 1:
                logger.warning(f"Unable to load configuration file, attempting automatic overwrite ({self.fault_retry_count}/{self.fault_retry_threshold})")
            else:
                logger.debug(f"Creating config file at '{self.path}'...")

            self.update_keys()
            self.load()

    def get(self, key_path, fallback=None):
        context = self.data
        parts = key_path.split(".")
        for i, key in enumerate(parts):
            if not isinstance(context, Mapping):
                return fallback
            context = context.get(key, {} if i + 1 != len(parts) else fallback)
        return context

    def set(self, key_path, value):
        keys = key_path.split(".")
        context = self.data

        for i, key in enumerate(keys):
            if i < len(keys) - 1:
                if key not in context or not isinstance(context[key], Mapping):
                    context[key] = tomlkit.table()
                context = context[key]
            else:
                context[key] = value

        self.save()

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            tomlkit.dump(self.data, f)

    def verify_keys(self):
        if not self.template:
            return True
        for key in self.template:
            if key not in self.data:
                return False
        return True

    def update_keys(self):
        if self.template:
            for key, value in self.template.items():
                if key not in self.data:
                    self.data.add(key, value)
        self.save()

    def __call__(self, key_path):
        return self.get(key_path)

    def __getitem__(self, key_path):
        return self.get(key_path)

    def __setitem__(self, key_path, value):
        return self.set(key_path, value)

    def __str__(self):
        return tomlkit.dumps(self.data)