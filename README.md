# Nautica API

A lightweight Python API framework built on [Starlette](https://www.starlette.io/), with file-based routing, request validation, and a simple decorator-driven interface.

---

## Installation

```bash
git clone https://github.com/xellu/nautica-api.git
cd nautica-api
pip install .
```

---

## Quick Start

```bash
# Create a new project
nautica create my-project
cd my-project

# Start the server
nautica run
```

The server starts on `http://127.0.0.1:8100` by default.

---

## File-Based Routing

Routes live in `src/http/`. Each `.py` file in that directory is automatically imported and its routes registered.

The file path maps directly to the URL path:

| File | URL prefix |
|------|-----------|
| `src/http/+root.py` | `/` |
| `src/http/users.py` | `/users` |
| `src/http/admin/stats.py` | `/admin/stats` |

`+root.py` always maps to the root of its directory.

---

## Defining Routes

Use `HTTP.<Method>(path)` to register a handler. The path argument sets the final segment of the URL — if omitted, the function name is used.

```python
from napi.http import HTTP, Context, Reply, Error, Require, StatusCodes

@HTTP.GET("/hello")
async def hello(ctx: Context):
    return Reply(message="Hello, world!")
```

Available methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `CONNECT`, `TRACE`

### Path Parameters

Use Starlette's `{param:type}` syntax in the route path, then declare a matching argument in your function:

```python
@HTTP.GET("/users/{name:str}")
async def get_user(ctx: Context, name: str):
    return Reply(name=name)
```

---

## Request Validation

`@HTTP.Require` declares what a request must include before your handler is called. If validation fails, Nautica automatically returns a `422 Unprocessable Content` response.

```python
@HTTP.GET("/search")
@HTTP.Require(
    query={"q": str, "limit": int}
)
async def search(ctx: Context):
    return Reply(query=ctx.query["q"], limit=ctx.query["limit"])
```

Validation targets: `body`, `query`, `headers`, `cookies`

### Built-in Validators

Instead of a plain type, you can use a `Requirement` for richer validation:

| Validator | Description |
|-----------|-------------|
| `Require.AnyOf("a", "b")` | Value must be one of the given options |
| `Require.AnyTypeOf(str, int)` | Value must match one of the given types |
| `Require.ExactMatch("value")` | Value must equal exactly |
| `Require.RegExMatch(r"\d+")` | Value must match the regex |

```python
@HTTP.GET("/items")
@HTTP.Require(
    query={"sort": Require.AnyOf("asc", "desc"), "id": Require.RegExMatch(r"^\d+$")}
)
async def get_items(ctx: Context):
    ...
```

---

## Responses

### JSON (dict)

```python
return Reply(name="Martin", age=25)
# → {"name": "Martin", "age": 25}
```

### JSON (array)

```python
return Reply({"name": "Martin"}, {"name": "Lucy"})
# → [{"name": "Martin"}, {"name": "Lucy"}]
```

> Mixing positional and keyword arguments raises a `TypeError`.

### With a status code

```python
return Reply(id=42), StatusCodes.CREATED   # 201
```

### Errors

```python
return Error(404)
return Error(StatusCodes.CONFLICT, "User already exists")
```

### Cookies

```python
reply = Reply(ok=True)
reply.SetCookie("session") \
     .value("abc123") \
     .maxAge(3600) \
     .httpOnly() \
     .secure() \
     .build()
return reply
```

---

## Request Context

Your handler receives a `ctx: Context` object with the validated request data:

| Attribute | Type | Description |
|-----------|------|-------------|
| `ctx.query` | `dict` | Query string parameters |
| `ctx.body` | `dict` | JSON body fields |
| `ctx.headers` | `dict` | Request headers |
| `ctx.cookies` | `dict` | Request cookies |
| `ctx.params` | `dict` | URL path parameters |
| `ctx.clientIp` | `str` | Client IP address |
| `ctx.url` | `URL` | Full request URL |
| `ctx.request` | `Request` | Raw Starlette request |

---

## Configuration

Edit `config/nautica.toml` to configure the server:

```toml
[nautica]
debug = true

[http]
host = "127.0.0.1"   # Use 0.0.0.0 to expose publicly
port = 8100
realIPHeader = "X-Real-IP"  # Set to "" to use the raw connecting IP

[http.static]
enabled = false
endpoint = "/static"
directory = "path/to/directory"
```

---

## CLI Reference

| Command | Description |
|---------|-------------|
| `nautica create <name>` | Scaffold a new project |
| `nautica run` | Start the server |
| `nautica load` | Regenerate config files |

---

## Project Structure

```
my-project/
├── config/
│   └── nautica.toml
├── src/
│   └── http/
│       └── +root.py      # Routes at /
├── plugins/              # Optional service plugins
└── .logs/
```
