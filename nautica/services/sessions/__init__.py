from ..logger import LogManager

logger = LogManager("Services.Sessions")

class SessionManager:
    def __init__(self):
        self.db = None