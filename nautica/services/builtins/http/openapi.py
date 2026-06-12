from ....models.Service import Service
from ....manager import Config, ConfigBuilder, Logger
from ....services import Services

import yaml

class OpenAPIGenerator(Service):
    def onInstall(self):
        Config.Update("nautica",
            ConfigBuilder() \
                .add("http.docs", False, "Generate OpenAPI Docs and expose them at /nautica:docs") \
                .build()        
        )
    
    def isEnabled(self):
        return Config("nautica")["services.http"]
    
    def onSetup(self, registry):
        if not registry.get("Shell"): return
        
        from ...builtins.shell.decorator import RegisterCommand

        @RegisterCommand("mkopendocs", description="Generates OpenAPI Docs and saves it")
        async def mk_docs():
            self.createDocs()
        
    def onStart(self, registry):
        if not Config("nautica")["http.docs"]:
            return
        
        self.createDocs()
    
    def createDocs(self):
        from .router import HTTPRouter
        
        router: HTTPRouter = Services.get("HTTPRouter")
        for r in router.routes:
            print(r.path)
    
Service.Export(OpenAPIGenerator, depends_on=["HTTPRouter", "Shell?", "HTTPServer:after"])