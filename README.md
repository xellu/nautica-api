# Nautica V3

![PyPI Version](https://img.shields.io/pypi/v/nautica?cacheSeconds=3600)
![Python](https://img.shields.io/pypi/pyversions/nautica?cacheSeconds=3600)
![License](https://img.shields.io/pypi/l/nautica?cacheSeconds=3600)
![PyPI Downloads](https://img.shields.io/pypi/dm/nautica?cacheSeconds=3600)

Nautica3 is a backend platform for Python. It gives you a managed runtime environment with a service registry, lifecycle system, CLI, and built-in tools, saving you time from putting your app together and giving you more time to build it.


## Features
- [**Service Registry**](https://github.com/xellu/nautica-api/wiki/Service-Registry)
A System for managing plugins and their lifecycle and runtime. You can install 3rd party packages from [the Package Registry](https://napm.xellu.xyz/), or drop in `.py` files into `plugins/`.

- **Built-in Services**
Includes the [HTTP](https://github.com/xellu/nautica-api/wiki/Builtin-Services:-HTTP) and [WebSocket](https://github.com/xellu/nautica-api/wiki/Builtin-Services:-WebSockets) server, scheduler and more. Everything can be configured or disabled entirely.

- [**Config Manager**](https://github.com/xellu/nautica-api/wiki/Config-Manager)
A TOML configuration system with auto key management, live read and writes.

- [**Log Manager**](https://github.com/xellu/nautica-api/wiki/Log-Manager)
Provides a readable console and file output. Automatically resolves module from which it is being called.

- [**Shell**](https://github.com/xellu/nautica-api/wiki/Builtin-Services:-Shell)
Gives you a way to interact with the server. Additionally you can use the TUI to view all the workers and running threads.


And more! [Learn more](https://github.com/xellu/nautica-api/wiki)

***

I made Nautica because I was solving the same problems in my projects, those being: configs, logging, figuring out startup orders, not to mention the validation boilerplate on every route. Because of this I made Nautica V2, which solved many of these issues, and V3 to improve on the idea.

## Get Started

Firstly, install Nautica:
```bash
pip install nautica
```

To create a project, use the Nautica CLI ([docs](https://github.com/xellu/nautica-api/wiki/CLI-Reference)):
```bash
nautica create my-project --demo
cd my-project
nautica run
```

<br>
Or continue working on an already existing project by installing it:

```bash
cd my-project
nautica install
```
*This will automatically download all needed packages and create associated configuration files*/

***

## How Nautica Compares

### Benchmark Performance

| Framework | Requests/Second | Avg Latency | Overall |
| --------- | --------------- | ----------- | ------- |
| Nautica3  | `3929`          | `2.5ms`     | *Baseline*                       |
| FastAPI   | `3154`          | `3.2ms`     | 24% slower, 19% higher latency   |
| Flask     | `75`            | `132.6ms`   | 50x slower, 98% higher latency |

> *Ran with 10 workers, for 10 seconds. Logging disabled, no-op routes.*

### Code Complexity

Similarly to SvelteKit, Nautica defines the route names for you. This helps to reduce boilerplate (see Flask and FastAPI examples), improve readability, and helps with naming conventions

#### Nautica3
```py
# file: src/http/api/v1/auth.py
from napi.http import HTTP, Context, Reply, Error
from somewhere import username, password

@HTTP.POST()
@HTTP.Require(body = {"username": str, "password": str})
def login(ctx: Context):
    if ctx.body["username"] == username and ctx.body["password"] == password:
        return Reply(ok=True)
    raise Error(401, "Invalid credentials")
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

### Flexibility


#### Request Validation
FastAPIs Pydantic models are fine..
```py
from pydantic import BaseModel

class ListUsersModel(BaseModel):
    format: str
    limit: int

@app.get("/api/users")
async def list_users(body: ListUsersModel):
    ...
```

But Nautica's Requirement system gives you more freedom:

```py
from napi.http import HTTP, Context, Require

@HTTP.POST()
@HTTP.Require( body = {"format": Require.AnyOf("dict", "list"), "limit": int} )
async def users(ctx: Context):
    ...
```
Which gives you access to default type checking + 6 `Requirement` validators:

`AnyOf(*options: any)`, `AnyTypeOf(*types: type)`, `ExactMatch(match: any)`, `RegExMatch(regex: str)`, `File(max_size?: int, mime?: str)` and `ListOf(obj: type | dict | Requirement, max_length?: int, max_length?: int)`.

> You can implement your custom validators on top of the system, [learn more on the wiki](https://github.com/xellu/nautica-api/wiki/Requirement-Validators#custom-validators).


#### Response Validation

Similarly, FastAPI uses type hints to determine the response of a route..

```py
from pydantic import BaseModel

class AuthResponse:
    session: str

@app.post("api/auth/login")
def login(body: LoginBody) -> AuthResponse:
    ...
```

Nautica instead uses a decorator-based approach:
```py
from napi.http import HTTP, Context, Error, ReplyModel

@HTTP.POST()
@HTTP.Responses(
    ReplyModel(200, {"session": str}),
    Error(401)
)
def login(ctx: Context):
    ...
```

If you want to prevent faulty responses, you can use the **strict** mode:

```py
@HTTP.Responses(
    ...,
    strict = True
)
# Cancels all responses that don't conform to a schema defined above
```

