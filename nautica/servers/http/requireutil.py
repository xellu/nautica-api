import json

import flask
from flask import make_response, Request

def RawReply(**kwargs):
    return kwargs

class Response:
    def __init__(self, content: dict, ok: bool = True):
        self.content = content
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

    def validate(self, data: dict):
        for k, v in self.kwargs.items():
            if k not in data.keys():
                return Response(RawReply(error=f"Missing required value for {k}"), False)

            if type(data[k]) != v:
                return Response(RawReply(error=f"Invalid type for {k}, provided {type(k).__name__}, expected {v.__name__}"), False)
        
        return Response({})

    def body(self):
        data = self.request.get_data(as_text=True)

        try:
            data = json.loads(data)
        except:
            return Response(RawReply(error="Unable to parse request body"), False)    
        
        res = self.validate(data)
        if not res.ok:
            return res
        
        return Response(data)

    def headers(self):
        data = self.request.headers

        res = self.validate(data)
        if not res.ok:
            return res
        
        return Response(data)
    
    def query(self):
        data = self.request.args

        res = self.validate(data)
        if not res.ok:
            return res
        
        return Response(data)
    
    def form(self):
        data = self.request.form

        res = self.validate(data)
        if not res.ok:
            return res
        
        return Response(data)
    
    def cookies(self):
        data = self.request.cookies
        
        res = self.validate(data)
        if not res.ok:
            return res
        
        return Response(data)
    
    #legacy code from doorsmc webserver api
    def _legacyInvalidate(self, payload, **args):
        """
        :payload: a payload to check\n:args: keys to check the payload for\n\nChecks if a payload is valid
        """
        max_limit = 1024

        for key in args:
            if key not in payload:
                return True
            if type(payload[key]) != args[key]:
                return True
            if len(str(payload[key])) > max_limit:
                return True
            
        return False

    def _legacyFetch(self, request):
        """
        :request: a flask request object to fetch data from\n\nLoads data from a request
        """
        try:
            data = json.loads(request.get_data())
            return data
        except:
            return {}
        
    def body_legacy(self):
        """
        (!) DEPRECATED: Use .body() instead!!!

        :request: a flask request object to fetch data from\n
        :args: keys to check the request payload for\n\n
        Loads data from a request and checks if it is valid (returns None if invalid)\n
        Example:
            request body = `{"hello": "world"}`\n
            `Require(request, hello=str)` -> `{"hello": "world"}`\n
            `Require(request, world=str)` -> `None`
        """
        data = self._legacyFetch(self.request)
        if self._legacyInvalidate(data, self.kwargs):
            return None
        return data