import json

from fastapi import Request

def RawReply(**kwargs):
    return kwargs

class Response:
    def __init__(self, content: dict, ok: bool = True):
        self.content = dict(content)
        self.ok = ok


class Require:
    def __init__(self, request: Request, **kwargs) -> Response:
        """
        :param request: The request object from Flask
        :param kwargs: The required keys and their types

        Example:
            Require(request, name=str, age=int)
        
        Returns:
            type: Response
            Response.content: The data from the request
            Response.ok: Whether the request was valid or not

        Functions:
            .body(): Get the request body as JSON
            .headers(): Get the request headers
            .query(): Get the request query
            .form(): Get the request form
            .cookies(): Get the request cookies

        This will require the request to have a JSON body with the keys "name" and "age" with the types str and int respectively.

        The types can be any type, such as str, int, float, dict, list, etc.
        Required keys can be in the body, headers, query, or form of the request.

        This will treat the request as a JSON body by default.

        """
        self.request = request
        self.kwargs = kwargs

    async def _get_body(self):
        try:
            data = await self.request.json()
        except:
            data = {}
        return data

    async def validate(self, data: dict, _in: str = "field"):
        for k, v in self.kwargs.items():
            if k not in data:
                return Response(RawReply(error=f"Missing required value for '{k}' in {_in}"), False)

            if not isinstance(data[k], v):
                return Response(
                    RawReply(
                        error=f"Invalid type for '{k}' in {_in}, provided {type(data[k]).__name__} - expected {v.__name__}"
                    ),
                    False
                )
        return Response({})

    async def body(self):
        data = await self._get_body()
        res = await self.validate(data, "body")
        if not res.ok:
            return res
        return Response(data)

    async def body_soft(self):
        data = await self._get_body()
        if not data:
            return Response({})
        res = await self.validate(data, "body")
        if not res.ok:
            return res
        return Response(data)

    async def headers(self):
        data = dict(self.request.headers)
        res = await self.validate(data, "headers")
        if not res.ok:
            return res
        return Response(data)

    async def query(self):
        data = dict(self.request.query_params)
        res = await self.validate(data, "query")
        if not res.ok:
            return res
        return Response(data)

    async def form(self):
        form_data = await self.request.form()
        data = dict(form_data)
        res = await self.validate(data, "form")
        if not res.ok:
            return res
        return Response(data)

    async def cookies(self):
        data = dict(self.request.cookies)
        res = await self.validate(data, "cookies")
        if not res.ok:
            return res
        return Response(data)
    
class RequestObjSubstitute:
    def __init__(self):
        self.body = {}
        self.headers = {}
        self.args = {}
        self.form = {}
        self.cookies = {}
    
    def get_data(self, as_text: bool = False):
        return json.dumps(self.body)