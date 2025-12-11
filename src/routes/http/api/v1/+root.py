import time

from nautica.api.http import (
    Request,
    Require,
    Reply,
    Error,
    Context
)

@Request.GET()
@Require.query(a=str)
def test(ctx: Context):
    return Reply(ip=ctx.request.remote_addr, args=ctx.args.toDict(), took=time.time()-ctx.created_at)
