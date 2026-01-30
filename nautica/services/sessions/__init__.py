from ..logger import LogManager
from ..database.xeldb import XelDB

logger = LogManager("Services.Sessions")

class SessionManager:
    def __init__(self, path):

        self.db = XelDB(path, primary_key="sessionId")