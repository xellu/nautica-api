import json
import os

from ..logger import LogManager

logger = LogManager("Services.Config.Helper")

class SubConfig:
    def __init__(self, path: str, template: dict | None = None, max_retries: int = 3):
        """
        Initialize a Config object.

        Args:
            path (str): The path to the configuration file.
            template (dict | None): The template for the configuration file.

        Returns:
            None
        """
        self.fault_retry_threshold = max_retries
        self.fault_retry_count = 0

        self.path = path.replace(".template.json", ".config.json")
        self.template = template

        self.data = {}
        self.load()

    def load(self):
        """
        Load the configuration data from the file.

        If the file does not exist, it will be created.

        Returns:
            None
        """
        try:
            with open(self.path, 'r') as file:
                self.data = json.load(file)

        except Exception as e:
            self.fault_retry_count += 1

            if self.fault_retry_count >= self.fault_retry_threshold:
                logger.error(f"Unable to load configuration file, automatic overwrite aborted (max retries exceeded)")
                return

            logger.warning(f"Unable to load configuration file, attempting automatic overwrite ({self.fault_retry_count}/{self.fault_retry_threshold})")

            self.update_keys()
            self.load()
    
    def get(self, key_path, fallback=None):
        # {
        #     "framework": {
        #         "devMode": True
        #     }
        # }
        # .get("framework.devMode") -> True
        context = self.data.copy() 
        for i, key in enumerate(key_path.split(".")):
            if not isinstance(context, dict):
                return fallback
                
            context = context.get(key, {} if i+1 != len(key_path.split('.')) else fallback)
            
        return context
    
    def set(self, key_path, value):
        # .set("framework.devMode", True)
        keys = key_path.split(".")
        context = self.data

        for i, key in enumerate(keys):
            if i < len(keys) - 1:
                if key not in context or not isinstance(context[key], dict):
                    context[key] = {}
                context = context[key]
            else:
                context[key] = value
                
        self.save()
    
    def __call__(self, key_path):
        return self.get(key_path)
    
    def __getitem__(self, key_path):
        return self.get(key_path)
    
    def __setitem__(self, key_path, value):
        return self.set(key_path, value)
    
    def __str__(self):
        return str(self.data)
    
    def save(self):
        """
        Save the configuration data to the file.

        Returns:
            None
        """
        with open(self.path, 'w') as file:
            json.dump(self.data, file, indent=4)
    
    def verify_keys(self):
        """
        Verify that the configuration file is valid.

        Returns:
            True if the configuration file is valid, otherwise False.
        """

        for key in self.template:
            if key not in self.data:
                return False

        return True
    
    def update_keys(self):
        """
        Update the configuration file with the keys.

        Returns:
            None
        """
        for key, value in self.template.items():
            if key not in self.data:
                self.data[key] = value

        self.save()