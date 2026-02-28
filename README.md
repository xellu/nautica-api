[!image](https://xellu.xyz/api/v2/files/2284f4dfffa64b038aaf816cde609731-531DLxwU4vNT.png)

# Nautica API
A Backend platform for Python, made for development experience and speed.

## What is this?
Nautica is a full backend platform for Python. It comes with an HTTP and WebSocket server, config system, logging, database support, and other built-in services all in one framework. Project structure is very similar to
**SvelteKit**, with **filesystem-based** routing, shared code in `src/lib` and asset files in `src/assets`. Think it as as "SvelteKit for backend".

It is made to simplify routing and reduce endpoint boilerplate:
**Before:**
```py
import json
from flask import request
from somewhere import App

@App.route("/api/v1/example", methods=["GET"])
def say_hello():
    query = request.args
    if not query:
        return json.dumps({"error": "No query parameters provided"}), 400
    if not query.get("hello"):
        return json.dumps({"error": "Query is missing a required argument 'hello'"}), 400
    if not isinstance(query.get("hello"), str):
        return json.dumps({"error": "'hello' argument must be a string"}), 400

    return json.dumps({"hello": query.get("hello")})
``` 

**After:**
```py
from nautica.api import Request, Require, Context, Reply

@Request.GET()
@Require.query(hello=str)
def example(ctx: Context):
    return Reply(hello=ctx.query["hello"])
```

This makes the code more simple and readable, allowing you to focus on development, and not on data validation, and other chores.
- For example, with the `@Require` decorator, you don't need to stress about missing fields - because if they're missing, the request fails before reaching your endpoint code.

## Installation
1. Download `https://github.com/xellu/nautica-api/releases/download/<VERSION>/nautica_api-<VERSION>.tar.gz`
2. and install it as a system package by using `python3 -m pip install nautica_api-<VERSION>.tar.gz`
3. Run it with `nautica`, `python3 -m nautica` (or `py -m nautica` on windows)

# Usage
Documentation can be found here: https://github.com/xellu/nautica-api/wiki