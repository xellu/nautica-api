from ....models.Service import Service
from ....manager import Config, ConfigBuilder, Logger
from ....services import Services
from ....ext.Util import randomStr, stripUnicode, unwrapToml
from ....ext.Path import getRoot
from ....ext.StatusCodes import getMessage
from ....models.Http import RouteRequirements, ErrorReply
from ....models.Requirements import serializeIntoComponent, dictToComponent

import yaml

class OpenAPIGenerator(Service):
    def onInstall(self):
        # Disabled for now
        # TODO: figure out how to do this
        
        # Config.Update("nautica",
        #     ConfigBuilder() \
        #         .add("http.docs", False, "Generate OpenAPI Docs and expose them at /nautica:docs") \
        #         .build()        
        # )
        
        Config.New("openapi", 
            ConfigBuilder() \
                .add("info.title", "Nautica API", "The name to show in the docs") \
                .add("info.version", "1.0.0", "Version of your API") \
                .add("servers", [{"url": "http://127.0.0.1", "description": "Development"}], "API Host; replace with your IP/Domain")
                .build()     
        )
    
    def isEnabled(self):
        return Config("nautica")["services.http"]
    
    def onSetup(self, registry):
        if not registry.get("Shell"): return
        
        from ...builtins.shell.decorator import RegisterCommand

        @RegisterCommand("oapidocs", description="Generates OpenAPI Documentation and saves it")
        async def mk_docs():
            docs = self.createDocs()
            with open("openapi.yaml", "w") as f:
                f.write(
                    yaml.dump(unwrapToml(docs), sort_keys=False, allow_unicode=True)
                )
                
            Logger.ok("Docs saved to 'openapi.yaml'")
        
    def onStart(self, registry):
        if not Config("nautica")["http.docs"]:
            return
        
        self.createDocs()
    
    def createDocs(self):
        from .router import HTTPRouter
        
        docs = {
            "openapi": "3.1.0",
            "info": {
                "title": str(Config("openapi")["info.title"]),
                "version": str(Config("openapi")["info.version"]),
            },
            "servers": unwrapToml(Config("openapi")["servers"]),
            "paths": {}
        }
        
        router: HTTPRouter = Services.get("HTTPRouter")
        for r in router.routes:
            if r.path not in docs["paths"].keys():
                docs["paths"][r.path] = {}
                
                
            reqs: RouteRequirements | None = r.getRequirements()

            operation = {
                "summary": r.getFunc().__name__.replace("_", " ").capitalize(),
                "parameters": [],
            }

            if reqs:
                for name, schema in (reqs.getQuery() or {}).items():
                    operation["parameters"].append({
                        "name": name,
                        "in": "query",
                        "required": True,
                        "schema": serializeIntoComponent(schema)
                    })
                for name, schema in (reqs.getHeaders() or {}).items():
                    operation["parameters"].append({
                        "name": name,
                        "in": "header",
                        "required": True,
                        "schema": serializeIntoComponent(schema)
                    })
                for name, schema in (reqs.getCookies() or {}).items():
                    operation["parameters"].append({
                        "name": name,
                        "in": "cookie",
                        "required": True,
                        "schema": serializeIntoComponent(schema)
                    })

                #body
                body = reqs.getBody()
                files = reqs.getFiles()

                if body or files:
                    if body:
                        schema = dictToComponent(body)
                    else:
                        schema = {"type": "object", "required": [], "properties": {}}
                    
                    if files:
                        encoding = {}
                        for fname, freq in files.items():
                            schema["properties"][fname] = {"type": "string", "format": "binary"}
                            schema["required"].append(fname)
                            if freq.mime:
                                encoding[fname] = {"contentType": ", ".join(freq.mime)}
                        
                        operation["requestBody"] = {
                            "required": True,
                            "content": {
                                "multipart/form-data": {
                                    "schema": schema,
                                    **({"encoding": encoding} if encoding else {})
                                }
                            }
                        }
                    else:
                        operation["requestBody"] = {
                            "required": True,
                            "content": {
                                "application/json": {"schema": schema }
                            }
                        }
            
            #reply models
            original = r.getFunc().__wrapped__ if hasattr(r.getFunc(), "__wrapped__") else r.getFunc()
            reply_models = getattr(original, "_replyModel", None)

            if reply_models:
                operation["responses"] = {}
                for model in reply_models:
                    if isinstance(model, int):
                        operation["responses"][str(model)] = {"description": getMessage(model) or str(model)}
                    else:
                        shape = serializeIntoComponent(model.shape) if not isinstance(model.shape, ErrorReply) else {}
                        operation["responses"][str(model.status_code)] = {
                            "description": getMessage(model.status_code) or str(model.status_code),
                            "content": {"application/json": {"schema": shape}} if shape else {}
                        }
            else:
                operation["responses"] = {"200": {"description": "OK"}}

            docs["paths"][r.path][r.getMethod().lower()] = operation

        return docs
    
Service.Export(OpenAPIGenerator, depends_on=["HTTPRouter", "HTTPConfig", "Shell?", "HTTPServer:after"])