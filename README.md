# Nautica API

## Features
| Feature             | Status     |
|---------------------|------------|
| HTTP Server         | finished   |
| SocketIO Server     | finished   |
| WebSocket Server    | maybe      |

## App structure
```
src
|
|-routes
|   |-http (routes for the HTTP server)
|   |-ws (routes for the WebSocket server)
|   |-... (should match the `nautica/servers` dir)
|
|-lib (shared code)
```

## API Structure
```
nautica
|
|-api       - public development interface
|   |-http 
|   |-ws
|
|-servers       - internal server code
|   |-http
|   |-ws
|
|-services
|   |-database (mongo, xeldb)
|   |-config
|   |-shell
|   |-logger
|   |-events
|   |-sessions
|   |-ratelimiter (not yet)
|
|-ext
|   |-utils
|   |-static
|   |-require_util
|
|-runner
```

## Route Example

`src/routes/http/api/v1/auth.py`
```py
# /api/v1/auth/(func name)
from nautica.api.http import (
    Request,
    Require,
    Context,

    Reply,
    Error
)
from nautica.api import MongoDB

@Request.POST()
@Require.body(username=str, password=str)
def login(ctx: Context):
    user = MongoDB("test").find_one({"username": ctx.args.body["username"]})
    if not user or user["password"] != ctx.args.body["password"]:
        return Error("Access denied"), 401

    return Reply(), 200 #success 
```