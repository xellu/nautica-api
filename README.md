# Nautica API

## Features
| Feature             | Status     |
|---------------------|------------|
| HTTP Server         | WIP        |
| SocketIO Server     | planned    |
| WebSocket Server    | planned    |

## App structure
```
src
|
|-routes
|   |-http (routes pro http server)
|   |-io (routes pro socket io server)
|   |-ws (routes pro websocket server)¨
|   |-... (should match the `nautica/servers` dir)
|
|-lib (yk shared code nebo neco, jak ve svelte)
```

## Project Structure
```
nautica
|
|-api       - public development interface
|   |-http 
|   |-ws
|   |-io
|
|-servers       - internal server code
|   |-http
|   |-io
|   |-ws
|
|-services
|   |-database (mongo, xeldb)
|   |-config
|   |-shell
|   |-logger
|   |-events
|   |-sessions
|   |-ratelimiter
|
|-ext
|   |-utils
|   |-static
|   |-require_util
|
|-runner
```

taklze jak to bude fungovat bro:
1. preprocessor scanne vsechny files a:
    - najde vsechny required config keys (zpicuje te jestli tam vsechny nejsou - dynamic config yooo)
    - processne vsechny library importy
2. importne to vsechny src routes do server runtimu
3. startne to servery


`src/routes/http/api/v1/auth.py`
```py
# /api/v1/auth/(func name)

@http.post()
@ratelimit("12/minute")
def register(request):
    return Reply(error="not yet"), 500

# HTTP POST to /api/v1/auth/register -> {"error": "not yet"}, code 500
```
*all just flask under the hood*