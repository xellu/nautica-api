from nautica.api.ws import (
    Packet,
    Reply
)

@Packet.On("hello")
async def on_hello(payload):
    print(f"{payload=}")
    return Reply(hello="world")