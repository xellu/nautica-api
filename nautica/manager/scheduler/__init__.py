import time
import asyncio
from typing import Awaitable, Coroutine

from ...ext.Util import maybeAwait

class ScheduleLoop:
    def __init__(self, func, interval, lastRan):
        self.func = func
        self.interval = interval
        self.lastRan = lastRan

class ScheduleManager:
    def __init__(self):
        self.futures = [
            # (func, timestamp, args, kwargs)
        ]
        
        self.loops = [
            #ScheduleLoops
        ]
    
    def Await(self, coro: Awaitable):
        """Runs or schedules an async function"""
        
        try: #if there's an event loop already
            loop = asyncio.get_running_loop()
            asyncio.ensure_future(coro, loop=loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(coro)
            loop.close()
            
    def RunIn(self, func: callable | Coroutine, in_seconds: int|float, *args, **kwargs) -> None:
        """Run a function in X seconds"""
        if in_seconds <= 0: raise RuntimeWarning("Unable to schedule in the past")
        self.futures.append( (func, time.time() + in_seconds, args, kwargs) )
        
    def RunAt(self, func: callable | Coroutine, at_time: int|float, *args, **kwargs) -> None:
        if at_time < time.time(): raise RuntimeError("Unable to schedule in the past") 
        self.futures.append( (func, at_time, args, kwargs) )
        
    def SetInterval(self, func: callable | Coroutine, interval: int):
        self.loops.append(
            ScheduleLoop(func, interval, 0)
                                    #    ^ run immediately
        )
    
    def Interval(self, interval: int):
        def decorator(func):
            self.loops.append(ScheduleLoop(func, interval, 0))
            return func
        return decorator
        
        
    async def _loop(self):
        while True:
            #run futures
            to_remove = []
            for future in self.futures:
                func, run_at, args, kwargs = future
                
                if run_at > time.time(): continue
                
                await maybeAwait(func(*args, **kwargs))
                to_remove.append(future)
                
            for f in to_remove:
                self.futures.remove(f)
                
            #run loops
            for l in self.loops:
                if time.time() - l.lastRan < l.interval: continue
                
                await maybeAwait(l.func())
                l.lastRan = time.time()
            
            await asyncio.sleep(0.1)
                
Scheduler = ScheduleManager()