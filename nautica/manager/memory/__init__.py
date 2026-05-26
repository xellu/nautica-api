from copy import deepcopy

class MemoryManager:
    def __init__(self, limit: int = 50):
        self.limit = limit
        self.validator = None

        self._content: list[any] = []
        self._mirrors: list = []
        
        
    def setValidator(self, func: callable):
        self.validator = func
        
        for m in self._mirrors:
            m.validator = func #update mirrors as well
        
        return self
        
    def Add(self, entry: any) -> None:
        if self.validator:
            if not self.validator(entry):
                raise TypeError(f"Invalid entry provided: {entry}")
            
        self._content.append(entry)
        if len(self._content) > self.limit:
            self._content.pop(0)
            
        for m in self._mirrors: #add to mirrors
            m.Add(entry)
            
    def Recall(self, limit: int | None = None) -> list[any]:
        if limit == None or limit >= len(self._content):
            return deepcopy(self._content)
        
        return deepcopy(self._content[-limit:])
    
    def Forget(self):
        self._content = []
        
    def CreateMirror(self, copy_content: bool = True):
        m = MemoryManager(limit=self.limit)
        m.validator = self.validator
        
        if copy_content:
            m._content = self._content
        
        self._mirrors.append(m)
        return m
        
    def __len__(self):
        return len(self._content)