import pygame as pg
from .interface import Interface, get_interface
from .utils import PygameInit, QuitPygame, SwitchInterface


class Game:

    def __init__(self) -> None:
        
        self._interfaces: list[Interface] = []
        self._current_interface: Interface | None = None
        self._current_event_types: tuple[int, ...] = ()

    def register_interface(self, interface: Interface) -> None:

        if self._current_interface is None:
            self._current_interface = interface
        self._interfaces.append(interface)

    def pygame_init(self) -> PygameInit:
        return PygameInit()

    def run(self, screen: pg.Surface) -> None:

        pg.init()
        try:
            self._current_event_types = self._current_interface.get_event_types()
            self._run(screen)
        except QuitPygame: ...
        except KeyboardInterrupt:
            print()
        finally:
            pg.quit()
    
    def _run(self, screen: pg.Surface) -> None:

        clock = pg.time.Clock()
        while True:
            try:
                self._frame(screen, clock)
            except SwitchInterface as e:
                self._current_interface = get_interface(e.name)

    def _frame(self, screen: pg.Surface, clock: pg.time.Clock) -> None:
            
        for event in pg.event.get(self._current_event_types):
            self._current_interface.run_event(event)
        
        self._current_interface.run_frame(screen)

        clock.tick(60)
        pg.display.flip()
