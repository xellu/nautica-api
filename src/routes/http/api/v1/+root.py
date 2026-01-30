import time

from nautica.api.http import (
    Request,
    Require,
    Reply,
    Error,
    Context
)
from nautica.api import Config

@Request.GET()
def test(ctx: Context):
    print(f"{ctx.args}")
    return Reply(**ctx.args.toDict())