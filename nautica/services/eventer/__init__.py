import asyncio
from ...instances import EventManInstances

class EventManager:
    def __init__(self, bounce: bool = False):
        """
        A class representing an event system manager.

        Args:
            :bounce (bool): If True, will provide feedback if an event is emitted without any listeners
        """
        self.bounce = bounce
        self.events = {
            #"start": [func1, func2, func3],
        }
        self.globals = []

        EventManInstances.append(self)

    def on(self, event: str):
        """
        Decorator for registering an event listener.

        Args:
            event (str): The event to listen for.

        Returns:
            None
        """
        def wrapper(func):
            if event not in self.events:
                self.events[event] = []

            self.events[event].append(func)
            # print(f"Registered event listener for {event}")

        return wrapper
    listen = on
    observe = on
    
    def listen_all(self, func):
        """
        Register a global event listener.
        WARNING: Do not create event listeners with the same names, as they will be voided.

        Args:
            func: The function to register as a global event listener.

        Returns:
            None
        """

        # for gf in self.globals:
        #     if gf.__name__ == func.__name__:
        #         return

        self.globals.append(func)

    def signal(self, event: str, *args, **kwargs):
        """
        Emit an event.

        Args:
            event (str): The event to emit.

        Returns:
            Boolean: True if the event was emitted, False if not.
        """
        if event not in self.events:
            return False
        
        if self.bounce and len(self.events[event]) == 0:
            return False
        
        for func in self.events[event]:
            # print(f"calling {func.__name__} for {event}")
            func(*args, **kwargs)

        for func in self.globals:
            # print(f"calling global listener {func.__name__}")
            func(event, *args, **kwargs)

        return True
    emit = signal
    
    def signal_async(self, event: str, *args, **kwargs):
        """
        Emit an event asynchronously.
        
        Args:
            event (str): The event to emit.
            
        Returns:
            Boolean: True if the event was emitted, False if not.
        """
        if event not in self.events:
            return False
        
        if self.bounce and len(self.events[event]) == 0:
            return False
        
        for func in self.events[event]:
            asyncio.create_task(func(*args, **kwargs))
            
        for func in self.globals:
            asyncio.create_task(func(event, *args, **kwargs))
            
        return True
    emit_async = signal_async

    def detach(self, event: str, func):
        """
        Remove an event listener.

        Args:
            event (str): The event to remove the listener from.
            func: The function to remove.

        Returns:
            None
        """
        if event not in self.events:
            return

        self.events[event].remove(func)