from nautica.api.http import (
    Request,
    Reply,
    Require,
    ctx
)

@Request.GET("b")
def test():
    data = Require(ctx, hello=str).query()
    if not data.ok:
        return Reply(hello="no thank you"), 400
    return Reply(hello=data.content["hello"])