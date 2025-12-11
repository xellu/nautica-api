import threading
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database

from ..logger import LogManager

logger = LogManager("Services.Database.Mongo")

class MongoDBWrapper:
    """
    A class representing a database service.

    Attributes:
        config (ConfigManager): The configuration object for the database service.
        databases (str[]): A dictionary containing the loaded collections.
    """

    def __init__(self, config, eventer):
        self.config = config
        self.eventer = eventer
        
        self.client = None
        self.thread = threading.Thread(target=self.connect)

    def start(self):
        if not self.config.getMaster("services.database.mongoUri"):
            return logger.warn("MongoDB service is disabled")
            
        self.thread.start()
        logger.info("Connecting to database server")

    def stop(self):
        if self.thread.is_alive(): self.thread.join()
        logger.ok("Database connection closed")

    def connect(self) -> None:
            """
            Establishes a connection to the MongoDB database.

            Raises:
                Exception: If unable to establish connection to MongoDB.

            Returns:
                None
            """
            try:
                uri = self.config.getMaster("services.database.mongoUri")    
                self.client = MongoClient(uri, server_api=ServerApi('1'))

                try:
                    self.client.admin.command('ping')
                    logger.success("Database connection established")

                    self.eventer.signal("database.ready", self)

                except Exception as e:
                    self.eventer.signal("error", e, "Service.Database", str(e), fatal=True)
                    return

            except Exception as e:
                self.eventer.signal("error", e, "Service.Database", "Unable to establish connection to MongoDB", fatal=True)
                return

    def __call__(self, collection) -> Database:
        return self.client.get_database(collection)