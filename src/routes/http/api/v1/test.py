from nautica.api.http import (
    Request,
    Reply,
    Error,
    Context
)

@Request.GET("a")
def test(ctx: Context):
   return Reply(ip=ctx.request.remote_addr)