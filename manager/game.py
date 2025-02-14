import pygame as pg
from .interface import Interface, get_interface
from .event import Event
from .utils import PygameInit, QuitPygame, SwitchInterface, quit_pygame
from typing import Callable


class Game:

    def __init__(self, quit: bool = True) -> None:
        
        self._interfaces: list[Interface] = []
        self._current_interface: Interface | None = None

        self._event_types: tuple[int, ...] = ()

        self._events: dict[int, list[Event]] = {}
        self._frame = None

        if quit:
            self._events[pg.QUIT] = [Event(quit_pygame)]

    def event(self, event_type: int, params: tuple[str, ...] = (), **kwargs) -> Callable[[Callable], Callable]:

        def decorator(f: Callable) -> Callable:
            if event_type not in self._events:
                self._events[event_type] = []
            self._events[event_type].append(Event(f, params, **kwargs))
            return f

        return decorator
    
    def frame(self, func: Callable[[pg.Surface], None]) -> Callable:
        self._frame = func
        return func

    def register_interface(self, interface: Interface) -> None:

        if self._current_interface is None:
            self._current_interface = interface
        self._interfaces.append(interface)

    def pygame_init(self) -> PygameInit:
        return PygameInit()

    def run(self, screen: pg.Surface) -> None:

        pg.init()
        try:
            self._event_types = self._get_event_types()
            self._run(screen)
        except QuitPygame: ...
        except KeyboardInterrupt:
            print()
        finally:
            pg.quit()

    def _get_event_types(self) -> tuple[str, ...]:
        return tuple(set(*self._events.keys(), *self._current_interface.get_event_types()))
    
    def _run(self, screen: pg.Surface) -> None:

        clock = pg.time.Clock()
        while True:
            
            try:
                self._run_events()
                self._run_frame(screen)
            except SwitchInterface as e:
                self._current_interface = get_interface(e.name)
                self._current_event_types = self._get_event_types()

            clock.tick(60)
            pg.display.flip()

    def _run_events(self) -> None:

        for pygame_event in pg.event.get(self._event_types):
            for event in self._events.get(pygame_event.type, []):
                event.run(pygame_event)
                self._current_interface.run_event(pygame_event)

    def _run_frame(self, screen: pg.Surface) -> None:

        if self._frame is not None:
            self._frame(screen)
        self._current_interface.run_frame(screen)
