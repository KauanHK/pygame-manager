import pygame as pg
from .interface import BaseInterface, Interface, get_interface
from .event import Event
from .utils import PygameInit, QuitPygame, SwitchInterface, quit_pygame
from typing import Callable


class Game(BaseInterface):

    def __init__(self, quit: bool = True) -> None:
        
        super().__init__()
        self._interfaces: list[Interface] = []
        self._current_interface: Interface | None = None
        self._current_event_types: tuple[int, ...]
        self._init = False

        if quit:
            self._events.add(quit_pygame, pg.QUIT)

    def register_interface(self, interface: Interface) -> None:

        if self._current_interface is None:
            self._current_interface = interface
        self._interfaces.append(interface)

    def pygame_init(self) -> PygameInit:
        self._init = True
        return PygameInit()

    def run(self, screen: pg.Surface) -> None:

        if not self._init:
            pg.init()
        try:
            for interface in self._interfaces:
                interface.init()
            self._current_event_types = self.get_event_types()
            self._run(screen)
        except QuitPygame: ...
        except KeyboardInterrupt:
            print()
        finally:
            pg.quit()

    def get_event_types(self) -> tuple[str, ...]:
        return tuple((*self._event_types, *self._current_interface.get_event_types()))
    
    def _run(self, screen: pg.Surface) -> None:

        clock = pg.time.Clock()
        while True:
            
            try:
                self._run_events()
                self._run_frame(screen)
            except SwitchInterface as e:
                self._current_interface = get_interface(e.name)
                self._current_event_types = self.get_event_types()

            clock.tick(60)
            pg.display.flip()

    def _run_events(self) -> None:

        for pygame_event in pg.event.get(self._current_event_types):
            self.run_event(pygame_event)
            self._current_interface.run_event(pygame_event)

    def _run_frame(self, screen: pg.Surface) -> None:

        if self._frame is not None:
            self._frame(screen)
        self._current_interface.run_frame(screen)
