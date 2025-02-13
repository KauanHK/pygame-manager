import pygame as pg
from functools import wraps
from typing import Callable, Any


class Event:

    def __init__(self, func: Callable, params: tuple[str, ...] = (), **kwargs) -> None:

        self.func = func
        self.params = params
        self.kwargs = kwargs
        self._objects: list[object] = []

    def register_object(self, obj: object) -> None:
        self._objects.append(obj)

    def run(self, pygame_event: pg.event.Event) -> None:

        params = self._get_params(pygame_event)
        event_dict = pygame_event.dict
        objects = self._objects.copy()
        for k,v in self.kwargs.items():

            if callable(v):
                if not objects:
                    if not v(event_dict[k]):
                        return
                else:
                    for obj in objects:
                        if not v(obj, event_dict[k]):
                            objects.remove(obj)

            elif v != event_dict[k]:
                return

        if not objects:
            self.func(**params)
            return
        for obj in objects:
            self.func(obj, **params)

    def _get_params(self, pygame_event: pg.event.Event) -> dict[str, Any]:
        
        params = {}
        for param in self.params:
            params[param] = pygame_event.dict[param]
        return params
    
    def __repr__(self) -> str:
        return f'Event({self.func.__qualname__}{self.params}, kwargs = {self.kwargs})'


class Events:

    def __init__(self) -> None:

        self._events: dict[int, list[Event]] = {}
        self._owners: dict[str, list[Event]] = {}

    def add(self, func: Callable, event_type: int, params: tuple[str, ...] = (), **kwargs) -> None:

        event = Event(func, params, **kwargs)
        if event_type not in self._events:
            self._events[event_type] = []
        self._events[event_type].append(event)
        owner = '.'.join(func.__qualname__.split('.')[:-1])
        if owner not in self._owners:
            self._owners[owner] = []
        self._owners[owner].append(event)

    def register_cls(self, cls: type) -> None:

        original_init = cls.__init__
        @wraps(original_init)
        def __init__(*args, **kwargs) -> None:
            original_init(*args, **kwargs)

            for event in self._owners[cls.__qualname__]:
                event.register_object(args[0])

        cls.__init__ = __init__

    def get_event_types(self) -> tuple[str, ...]:
        return tuple(self._events.keys())

    def run(self, pygame_event: pg.event.Event) -> None:

        for event in self._events.get(pygame_event.type, []):
            event.run(pygame_event)

    def __repr__(self) -> str:
        return repr(self._events)
