import pygame as pg
from .event import Events
from typing import Callable, Self


class Interface:

    _objects: dict[str, Self] = {}

    def __init__(self, name: str) -> None:

        self._name = name
        self._events = Events()
        self._frame = None
        Interface._objects[name] = self

    def event(self, event_type: int, params: tuple[str, ...] = (), **kwargs) -> Callable:

        def decorator(f: Callable) -> Callable:
            self._events.add(f, event_type, params, **kwargs)
            return f

        return decorator
    
    def register_cls(self, cls: type) -> type:
        self._events.register_cls(cls)
        return cls
    
    def frame(self, frame: Callable) -> None:
        self._frame = frame

    def get_event_types(self) -> tuple[int, ...]:
        return self._events.get_event_types()

    def run_event(self, pygame_event: pg.event.Event) -> None:
        self._events.run(pygame_event)

    def run_frame(self, screen: pg.Surface) -> None:
        self._frame(screen)

    def __repr__(self) -> str:
        return f'Interface({self._name})'


def get_interface(name: str) -> Interface:

    if name not in Interface._objects:
        raise NameError(f"Interface '{name}' não existe.")
    return Interface._objects[name]
