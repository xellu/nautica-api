from .config import ConfigManager
from .config.builder import OptionBuilder as ConfigBuilder
from .logger import LogManager

Logger = LogManager()
Config = ConfigManager()