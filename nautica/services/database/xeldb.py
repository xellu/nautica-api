from ... import instances
from ...services.logger import LogManager

import os
import json
import zlib
import uuid
import time
import threading


class XelDB:
    def __init__(self, path, primary_key: str = None):
        self.path = path + ".xdb"
        self.primary_key = primary_key

        self.thread_running = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.unsaved = False

        self.data = {}
        self.data_keyed = {}

        if not os.path.exists(self.path):
            _dir = os.path.dirname(self.path)
            if _dir:
                os.makedirs(_dir)
            self.save()

        self.load()
        self.thread.start()
        instances.XelDBInstances.append(self)

    # ---------- persistence ----------

    def load(self):
        with self.lock:
            raw = open(self.path, "rb").read()
            raw = zlib.decompress(raw).decode("utf-8")
            self.data = json.loads(raw)
            
            if not self.primary_key:
                return
            
            for item in self.data.values():
                self.create_keyed_alt(item)

    def save(self):
        with self.lock:
            raw = json.dumps(self.data).encode("utf-8")
            raw = zlib.compress(raw)

            temp = self.path + ".tmp"
            with open(temp, "wb") as f:
                f.write(raw)
            os.replace(temp, self.path)

    def stop(self):
        self.thread_running = False
        self.thread.join()
        
    def _loop(self):
        _loop_lock = 5
        while self.thread_running:
            _loop_lock -= 1
            
            if _loop_lock > 0:
                continue        
            _loop_lock = 5
    
            if self.unsaved:
                self.save()
                self.unsaved = False
                
            time.sleep(1)
                
        self.save()
        
    def create_keyed_alt(self, item):
        if not self.primary_key: return
        
        key = item.get(self.primary_key)
        if key is None: return
        
        if self.data_keyed.get(key):
            raise KeyError(f"Duplicate primary key for '{key}' in item: {item}")
        
        self.data_keyed[key] = item.get("_id")

    #-----------db operations--------------
    def create(self, **item):
        try: json.dumps(item)
        except TypeError: raise ValueError("Item has to be JSON-serializable")

        with self.lock:
            item["_id"] = uuid.uuid4().hex
            self.data[item["_id"]] = item
            self.create_keyed_alt(item)
            
            return item["_id"]

    def filter(self, func):
        out = []
        for item in self.data.values():
            if func(item): out.append(item)
        
        return out

    def getByProp(self, property: str, value): #O(n)
        with self.lock:
            for _, item in self.data.items():
                if item.get(property) == value:
                    return item.copy()

    #using id ----------
    def getById(self, itemId: str):
        with self.lock:
            item = self.data.get(itemId)
            return item.copy() if item else None
    
    
    def setById(self, itemId: str, property: str, value) -> bool:
        with self.lock:
            self.unsaved = True

            item = self.data.get(itemId)
            if not item or property == "_id":
                return False

            #update primary key
            if self.primary_key and property == self.primary_key:
                old_key = item.get(self.primary_key)
                if old_key in self.data_keyed:
                    del self.data_keyed[old_key]
                self.data_keyed[value] = itemId

            item[property] = value
            return True


    def removeById(self, itemId: str) -> bool:
        with self.lock:
            self.unsaved = True

            item = self.data.pop(itemId, None)
            if not item:
                return False

            #remove primary key index
            if self.primary_key:
                key = item.get(self.primary_key)
                if key in self.data_keyed:
                    del self.data_keyed[key]

            return True

    #using primary key ----------
    def getByKey(self, primary_key):
        with self.lock:
            itemId = self.data_keyed.get(primary_key)
            if not itemId: return
            
            item = self.data.get(itemId)
            return item.copy() if item else None
    
    
    def setByKey(self, primary_key, property: str, value) -> bool:
        with self.lock:
            self.unsaved = True

            itemId = self.data_keyed.get(primary_key)
            if not itemId:
                return False

            item = self.data.get(itemId)
            if not item or property == "_id":
                return False

            #update primary key index
            if self.primary_key and property == self.primary_key:
                del self.data_keyed[primary_key]
                self.data_keyed[value] = itemId

            item[property] = value
            return True


    def removeByKey(self, primary_key) -> bool:
        with self.lock:
            self.unsaved = True

            itemId = self.data_keyed.pop(primary_key, None)
            if not itemId:
                return False

            item = self.data.pop(itemId, None)
            return item is not None