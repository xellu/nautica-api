from nautica.api.http import (
    Request
)

@Request.POST()
def test():
    print("test :)")
