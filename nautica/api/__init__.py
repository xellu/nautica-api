from .. import Core, _release
from ..services.sessions import SessionManager
from .http import (
    Context as _httpContext,
    
    Reply as _httpReply,
    ReplyList as _httpReplyList,
    Error as _httpError,
    
    Request as _httpRequest,
    Require as _httpRequire
)

Config = Core.Config
Eventer = Core.Eventer
MongoDB = Core.MongoDB
Sessions = SessionManager("sessions")

class HTTP:
    Context = _httpContext
    
    Reply = _httpReply
    ReplyList = _httpReplyList
    Error = _httpError
    
    Request = _httpRequest
    Require = _httpRequire