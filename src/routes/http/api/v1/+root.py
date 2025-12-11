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
@Require.query(key=str)
def test(ctx: Context):
    return Reply(**Config(ctx.args.query["key"]).data)
