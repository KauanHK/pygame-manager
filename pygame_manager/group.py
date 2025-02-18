from .interface import Interface, get_interface, Base
from .utils import FuncEvent
from functools import wraps
from typing import Callable


def _wrapper(func: FuncEvent) -> FuncEvent:
    @wraps(func)
    def wrapper(*args, **kwargs) -> None:
        if args[0].interface.is_activated:
            func(*args, **kwargs)
    return wrapper


class Group(Base):

    def __init__(self, *interfaces: Interface | str) -> None:
        
        super().__init__()
        for it in interfaces:
            if isinstance(it, str):
                it = get_interface(it)
            self._interfaces.append(it)

    def add(self, interface: Interface | str) -> None:
        if isinstance(interface, str):
            interface = get_interface(interface)
        self._interfaces.append(interface)

    def remove(self, interface: Interface | str) -> None:

        if isinstance(interface, str):
            interface = get_interface(interface)
        self._interfaces.remove(interface)

    def add_event(self, func: FuncEvent, event_type: int, params: tuple[str, ...] = (), **kwargs) -> None:

        for it in self._interfaces:
            it.add_event(func, event_type, params, **kwargs)

    def event(self, event_type: int, params: tuple[str, ...] = (), **kwargs) -> Callable[[FuncEvent], FuncEvent]:
    
        def decorator(f: FuncEvent) -> FuncEvent:
            for it in self._interfaces:
                it.add_event(f, event_type, params, **kwargs)
            return _wrapper(f)
        
        return decorator
    
    def register_cls(self, cls: type) -> type:

        self._set_cls(cls)

        original_init = cls.__init__
        @wraps(original_init)
        def __init__(*args, **kwargs) -> None:
            original_init(*args, **kwargs)
            for it in self._interfaces:
                it.add_object(args[0])

        cls.__init__ = __init__
        return cls

    def _set_cls(self, cls: type) -> None:
        for it in self._interfaces:
            it.set_cls(cls)
