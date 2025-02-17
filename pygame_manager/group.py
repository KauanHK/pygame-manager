from .interface import Interface, get_interface
from .utils import FuncEvent
from functools import wraps


class Group:

    def __init__(self, *interfaces: Interface | str) -> None:
        
        self._interfaces: list[Interface] = []
        for it in interfaces:
            if isinstance(it, str):
                it = get_interface(it)
            self._interfaces.append(it)


    def add(self, interface: Interface) -> None:
        self._interfaces.append(interface)

    def remove(self, interface: Interface | str) -> None:

        if isinstance(interface, str):
            interface = get_interface(interface)
        self._interfaces.remove(interface)

    def add_event(self, func: FuncEvent, event_type: int, params: tuple[str, ...] = (), **kwargs) -> None:

        for it in self._interfaces:
            it.add_event(func, event_type, params, **kwargs)

    def event(self, event_type: int, params: tuple[str, ...] = (), **kwargs):
    
        def decorator(f: FuncEvent) -> FuncEvent:
            
            for it in self._interfaces:
                it.add_event(f, event_type, params, **kwargs)

            return f
        
        return decorator
    
    def register_cls(self, cls: type) -> type:

        for it in self._interfaces:
            it._classes[cls.__qualname__] = cls
            it._objects[cls.__qualname__] = []

        original_init = cls.__init__
        @wraps(original_init)
        def __init__(*args, **kwargs) -> None:
            original_init(*args, **kwargs)
            for it in self._interfaces:
                it._objects[cls.__qualname__].append(args[0])

        cls.__init__ = __init__
        return cls
