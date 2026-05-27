# Nautica V3

Nautica V3 _(also referred to as Nautica API, Nautica3, N3)_ is a modular application framework built around a service registry. It provides you with a structured way to manage components of your applications, such as HTTP or Socket servers, background workers, etc.

> N3 is not just an HTTP framework — the HTTP server is one of many services. It's designed for applications that need to coordinate multiple components at once.

## What's Included
- **Service Registry** with dependency resolver
- **Lifecycle hooks** for install, start and shutdown
- TOML **Config system** with key management
- **Logger** with file output and memory
- **Shell** for interacting with services
- **TUI** for live logs, thread and worker inspection _(optional)_
- **Plugin system** for extending projects without modifying core code
- **HTTP API** built on Starlette + Uvicorn

---

I made N3 because I was solving the same problems in my projects, those being: configs, logging, figuring out startup orders, not to mention the validation boilerplate on every route. Because of this I made Nautica V2, which solved many of these issues, and V3 to improve on the idea.

## How HTTP API Compares

### Benchmark Performance

| Library | Requests/Second | Avg Latency | Overall |
| --- | --- | --- | --- |
| Nautica3 | `2271` | `4.4ms` | - |
| FastAPI | `2259` | `4.4ms` | 0.5% slower |
| Flask | `75` | `132.6ms` | 96% slower |

*Ran with 10 workers, for 10 seconds. Nautica3 matches FastAPI despite running additional middleware, requirement parsing, and logging on every request.*

### Code Complexity

Similarly to SvelteKit, Nautica defines the route names for you. This helps to reduce boilerplate (see Flask and FastAPI examples), improve readability, and helps with naming conventions

#### Nautica3
```py
# file: src/http/api/v1/auth.py
from napi.http import HTTP, Context, Reply
from somewhere import username, password

@HTTP.POST()
@HTTP.Require(body = {"username": str, "password": str})
def login(ctx: Context):
    if ctx.body["username"] == username and ctx.body["password"] == password:
        return Reply(ok=True)
    return Reply(ok=False, error="Invalid credentials"), 401
```

#### Flask
```py
# file: main.py
from flask import Flask, request
from flask.blueprints import Blueprint
import json
from somewhere import username, password

app = Flask(__name__)
v1auth = Blueprint("v1auth", __name__, url_prefix="/api/v1/auth")

@v1auth.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    if data.get("username") == username and data.get("password") == password:
        return json.dumps({"ok": True})
    return json.dumps({"ok": False, "error": "Invalid credentials"}), 401

app.register_blueprint(v1auth)
app.run(port=8101)
```

#### FastAPI
```py
# file: main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from somewhere import username, password

app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/v1/auth/login")
def login(body: LoginRequest):
    if body.username == username and body.password == password:
        return {"ok": True}
    raise HTTPException(status_code=401, detail="Invalid credentials")

uvicorn.run(app, port=8101)
```