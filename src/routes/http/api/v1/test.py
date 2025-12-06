from nautica.api.http import (
    Request,
    Require,
    Reply,
    Error,
    Context
)

@Request.GET("a")

def test(ctx):
   return Reply(args=ctx.args)