import pygame as pg
from functools import wraps
from typing import Callable, Any


class BaseEvent:

    def __init__(self, func: Callable, params: tuple[str, ...] = (), **kwargs) -> None:

        self.func = func
        self.params = params
        self.kwargs = kwargs

class Event(BaseEvent):

    def __init__(self, func: Callable, params: tuple[str, ...] = (), **kwargs) -> None:
        super().__init__(func, params, **kwargs)

    def run(self, pygame_event: pg.event.Event) -> None:

        params = self._get_params(pygame_event)
        event_dict = pygame_event.dict
        for k,v in self.kwargs.items():

            if callable(v):
                v_params = self._get_v_params(event_dict[k])
                if not v(*v_params):
                    return

            elif v != event_dict[k]:
                return

        self.func(**params)

    def _get_params(self, pygame_event: pg.event.Event) -> dict[str, Any]:
        
        params = {}
        for param in self.params:
            params[param] = pygame_event.dict[param]
        return params
    
    def _get_v_params(self, value: Any) -> tuple[Any] | tuple[object, Any]:

        if hasattr(self.func, '__self__'):
            return self.func.__self__, value
        return (value,)
    
    def __repr__(self) -> str:
        return f'Event({self.func.__qualname__}{self.params}, kwargs = {self.kwargs})'


class LoadingEvent(BaseEvent):

    def __init__(self, func: Callable, event_type: int, params: tuple[str, ...] = (), **kwargs) -> None:

        super().__init__(func, params, **kwargs)
        self.event_type = event_type

    def load(self, cls: type | None = None, objects: list[object] | None = None) -> list[Event]:

        if cls is None:
            return [Event(self.func, self.params, **self.kwargs)]
        
        events = []
        for obj in objects:
            events.append(Event(getattr(obj, self.func.__name__), self.params, **self.kwargs))
        return events


class Events:

    def __init__(self) -> None:

        self._owners: dict[str, list[LoadingEvent]] = {}
        self._classes: dict[str, type] = {}
        self._objects: dict[str, list[object]] = {}
        self._events: dict[int, list[Event]] = {}

    def add(self, func: Callable, event_type: int, params: tuple[str, ...] = (), **kwargs) -> None:

        event = LoadingEvent(func, event_type, params, **kwargs)
        owner = '.'.join(func.__qualname__.split('.')[:-1])
        if owner not in self._owners:
            self._owners[owner] = []
        self._owners[owner].append(event)

    def register_cls(self, cls: type) -> None:

        self._classes[cls.__qualname__] = cls
        self._objects[cls.__qualname__] = []

        original_init = cls.__init__
        @wraps(original_init)
        def __init__(*args, **kwargs) -> None:
            original_init(*args, **kwargs)
            self._objects[cls.__qualname__].append(args[0])

        cls.__init__ = __init__

    def init(self) -> None:

        self._events: dict[int, list[Event]] = {}
        for owner, loading_events in self._owners.items():
            for le in loading_events:

                if le.event_type not in self._events:
                    self._events[le.event_type] = []

                cls = self._classes.get(owner)
                objects = self._objects.get(owner)
                events = le.load(cls, objects)
                self._events[le.event_type].extend(events)
        
    def run(self, pygame_event: pg.event.Event) -> None:

        for event in self._events.get(pygame_event.type, []):
            event.run(pygame_event)

    def __repr__(self) -> str:
        return repr(self._events)
