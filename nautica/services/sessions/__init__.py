from ..logger import LogManager
from ..database.xeldb import XelDB
from ... import Core

from ...ext.utils import hashStr, randomStr

import time

logger = LogManager("Services.Sessions")

#yes i ai-generated the docs
class SessionManager:
    """
    Simple session management service backed by XelDB.

    Sessions are identified by a randomly generated, hashed session ID
    and can optionally expire after a specified amount of time.

    Each session stores:
    - sessionId: Unique session identifier (primary key)
    - refId: Reference to the associated object (e.g. user ID)
    - expire: UNIX timestamp when the session expires, or None if persistent

    Notes:
    - Designed for single-process usage
    - Expired sessions are removed lazily or via explicit cleanup
    """

    def __init__(self, path):
        """
        Initialize the session manager.

        If the session service is disabled via configuration, the manager
        will log the state and remain inactive.

        Args:
            path (str): Path to the session database (without extension).
        """
        if not Core.Config.getMaster("services.sessions.enabled"):
            logger.warn("Session service is disabled")
            return

        self.db = XelDB(path, primary_key="sessionId")
        
        self.delete_expired()

    def create(self, refId: str, expire: int | None = None) -> str:
        """
        Create a new session.

        Args:
            refId (str): Reference identifier associated with the session
                (for example, a user ID).
            expire (int | None): Number of seconds until the session expires.
                If None, the session does not expire.

        Returns:
            str: Generated session ID.
        """
        sessionId = hashStr(randomStr(64))
        self.db.create(
            sessionId=sessionId,
            refId=refId,
            expire=expire + time.time() if expire else expire
        )

        return sessionId

    def get(self, sessionId: str):
        """
        Retrieve the reference ID associated with a session.

        If the session does not exist or has expired, None is returned.
        Expired sessions are automatically removed.

        Args:
            sessionId (str): Session identifier.

        Returns:
            str | None: Associated reference ID if valid, otherwise None.
        """
        res = self.db.getByKey(sessionId)
        if not res:
            return None

        if res.get("expire") and time.time() > res.get("expire"):
            self.db.removeByKey(res["sessionId"])
            return None

        return res.get("refId")

    def delete(self, sessionId: str):
        """
        Delete a single session by its session ID.

        Args:
            sessionId (str): Session identifier.
        """
        self.db.removeByKey(sessionId)

    def delete_all(self, refId: str):
        """
        Delete all sessions associated with a given reference ID.

        Args:
            refId (str): Reference identifier (e.g. user ID).
        """
        to_delete = self.db.filter(lambda x: x["refId"] == refId)
        for session in to_delete:
            self.db.removeByKey(session["sessionId"])

    def delete_all_except(self, refId: str, except_ids: list[str]):
        """
        Delete all sessions for a reference ID except the specified ones.

        Args:
            refId (str): Reference identifier (e.g. user ID).
            except_ids (list[str]): List of session IDs to preserve.
        """
        to_delete = self.db.filter(lambda x: x["refId"] == refId)
        for session in to_delete:
            if session["sessionId"] in except_ids:
                continue
            self.db.removeByKey(session["sessionId"])

    def delete_expired(self):
        """
        Remove all expired sessions from the database.

        This method must be called manually or scheduled externally.
        """
        to_delete = self.db.filter(
            lambda x: x.get("expire") is not None and x.get("expire") < time.time()
        )
        for session in to_delete:
            self.db.removeByKey(session["sessionId"])