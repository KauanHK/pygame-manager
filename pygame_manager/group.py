from .interface import Interface, get_interface
from .utils import FuncEvent


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
    
    def register_cls(self, cls) -> None:
        
        for it in self._interfaces:
            it.register_cls(cls)
        return cls
