from nautica.api.http import (
    Request
)

@Request.GET("test_b")
def test():
    print("test :)")