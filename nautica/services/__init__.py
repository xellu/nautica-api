from ..models.Service import Service

class ServiceRegistry:
    def __init__(self):
        self.instances: set[Service] = set()
        
        self.autoStart = False
        
    def Create(self, serv: Service):
        if not isinstance(serv, Service):
            raise Exception(f"'{serv}' has type {type(serv).__name__}, required type: Service")
    
        for s in self.instances:
            if type(s).__name__ == type(serv).__name__:
                serv.onClose(f"Service for '{type(serv).__name__}' was already created")
                return
            
        self.instances.add(serv) #doesnt allow duplicates anyway
        # print(self.instances)
        
        if self.autoStart: serv.onStart()
        
    def Cancel(self, serv: Service):
        if serv in self.instances:
            self.instances.remove(serv)
            
    def Get(self, serviceName) -> Service | None:
        for s in self.instances:
            if type(s).__name__ == serviceName:
                return s
    
    def __getitem__(self, serviceName) -> Service | None:
        return self.Get(serviceName)
        
Registry = Services = ServiceRegistry()