import time

log_file = f"nautica_{time.strftime('%d_%m_%y__%H_%M_%S', time.localtime())}.log"


def banner(version, edition):
    return f"""
 ███████           █████       ████████████         ███  ██  ▄▄▄  ▄▄ ▄▄ ▄▄▄▄▄▄ ▄▄  ▄▄▄▄  ▄▄▄    ▄████▄ █████▄ ██ 
 █████████         █████▒▒ ████████████████████     ██ ▀▄██ ██▀██ ██ ██   ██   ██ ██▀▀▀ ██▀██   ██▄▄██ ██▄▄█▀ ██ 
 ███████████       █████▒▒▓██████▓▒▒▒▒▒▒▒██████▒    ██   ██ ██▀██ ▀███▀   ██   ██ ▀████ ██▀██   ██  ██ ██     ██ 
 ██████▒███████    █████▒▒▒▒▒▒▒▒▒▓████████████▓▓▒▒
 ██████▒▒░███████  █████▒▒▒  ▒▒▒▒▒█████████████▓▓   v{version}  ~  {edition} Edition
 ██████▒▒  ░████████████▒▒▒       ▒▒▒▒▒▒▒▒██████
 ██████▒▒    ░██████████▒▒▒███████  ▒▒▒▒▒██████▓▒▒  https://github.com/xellu/nautica-api
 ██████▒▒      ░████████▒▒▒ ██████████████████▒▒▒▒
 ██████▒▒        ░▓█████▒▒▒   ▒▒▒▓██████▓▓▒▒▒▒▒▒▒▒
   ▒▒▒▒▒▒           ▒▒▒▒▒▒▒     ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒"""
                                                             
GitIgnore = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[codz]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Nautica3
.logs/
config/

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py.cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
# .python-version

# pipenv
#Pipfile.lock

# UV
#uv.lock

# poetry
#poetry.lock
#poetry.toml

# pdm
#pdm.lock
#pdm.toml
.pdm-python
.pdm-build/

# pixi
.pixi

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.envrc
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#.idea/

# Abstra
# Abstra is an AI-powered process automation framework.
# Ignore directories containing user credentials, local state, and settings.
# Learn more at https://abstra.io/docs
.abstra/

# Visual Studio Code
# .vscode/

# Ruff stuff:
.ruff_cache/

# PyPI configuration file
.pypirc

# Cursor
.cursorignore
.cursorindexingignore

# Marimo
marimo/_static/
marimo/_lsp/
__marimo__/
"""
                                                          
ProjectExample = """
from napi.http import HTTP, Context, Reply, Error, Require, StatusCodes

#An Example Data set
DATASET = {
    "Martin": {
        "age": 25,
        "hobbies": ["Rock Climbing", "Skiing"]
    },
    "Lucy": {
        "age": 23,
        "hobbies": ["Doomscrolling", "Streaming on TikTok"]
    }
}

#Mark a function as a request, by using HTTP.<Method> decorator
@HTTP.GET("/users") #Set this as a GET request 
#          ^--- By providing a name, you can set the final component of the path. If it isn't provided, the function name will be used instead.

#Add fields that the request needs to complete successfully
@HTTP.Require(
    # v--- The query parameter in the URL (i.e. /users?format=<list/dict>)
    query = { "format": Require.AnyOf("list", "dict") } #This syntax works for all fields, that being: headers, cookies, body, query
                # ^       ^
                # |       |--- Define the data type, either use a "type" (e.g. str, int) or Requirement (e.g. Require.AnyOf(...), Require.RegExMatch(...))
                # |--- Define the name of the required parameter
                            
) #Create an async function with request context. Note that you can create a request even without context, but by doing so, you'll lose access to it
async def get_users(ctx: Context):
    if ctx.query["format"] == "dict":
        # raise Exception("Failed request")
        return Reply(**DATASET) #The Reply sends a JSON Dictionary when provided with kwargs (note the **)

    if ctx.query["format"] == "list":
        users = [{"name": key, **value} for key, value in DATASET.items()]
        return Reply(*users) #And sends a List as JSON, when provided with positional args (again, note the *)
                             #(!) Providing both args and kwargs raises a TypeError

    #No edgecase return needed, since if any other value for format will cause the request to fail before reaching your code

# ^--- Reach this endpoint by sending a GET request to http://127.0.0.1:8100/users?format=list (or ?format=dict) (Port may differ, based on your configuration in config/nautica.toml > http > port)

@HTTP.POST() #By not providing a route name, we default to using the function name instead (create_user in this case)
@HTTP.Require(
    body = {"name": str, "age": int}
    #        ^--- Fields expected in the JSON request body
    #             Same type-coercion rules apply as with query params
)
async def create_user(ctx: Context):
    name = ctx.body["name"]
    age = ctx.body["age"]

    if name in DATASET:
        raise Error(StatusCodes.CONFLICT, f"User '{name}' already exists")

    DATASET[name] = {"age": age, "hobbies": ["Debugging"]}
    return Reply(), StatusCodes.CREATED

# ^--- Reach this endpoint by sending a POST request to http://127.0.0.1:8100/create_user?name=<name>&age=<age>
"""