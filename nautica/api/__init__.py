from .. import Core, _release
from ..services.sessions import SessionManager

Config = Core.Config
Eventer = Core.Eventer
MongoDB = Core.MongoDB
Sessions = SessionManager("sessions")