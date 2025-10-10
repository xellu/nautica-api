from nautica import HTTP, Reply

@HTTP.get() #/api/v1/example/example
def example(request):
    return Reply(hello="world") #{"hello": "world"}, code 200 (if missing)


# route prefix is derived from file path + app config (preprocessor/loader convention)
@HTTP.post("/example") #/api/v1/example/example
def example_post(request):
    data = request.json
    return Reply(received=data) #{"received": data}, code 200 (if missing)
    # return Reply(error="not implemented"), 501
    # return Reply(error="bad request"), 400
    # return Reply(error="internal server error"), 500
    # return Reply(error="custom error message"), 418
