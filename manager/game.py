import pygame as pg
from .interface import Interface, get_interface


class QuitPygame(BaseException): ...

class PygameInit:

    def __enter__(self) -> None:
        pg.init()

    def __exit__(self, _, e, *args) -> None:

        if e:
            pg.quit()

class SwitchInterface(BaseException):

    def __init__(self, name: str, *args) -> None:
        self.name = name

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
