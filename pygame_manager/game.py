import pygame as pg
from ._interface import BaseInterface, NamedInterfaceRunner
from .types import FuncEvent, EventsClass
from .utils import QuitPygame, quit_pygame
from typing import Any, Callable, Self


class Game(BaseInterface):

    def __init__(
            self,
            fps: int = 60,
            quit: bool = True
    ) -> None:
        """Gerenciador de jogos pygame.
        
        Gerencia eventos e frames do jogo, dividindo o jogo de maneira modular em 
        interfaces e subinterfaces.

        :param int fps: FPS do jogo.
        :param bool quit: Se True, registra um evento para fechar o jogo.
        """

        super().__init__()
        self.fps = fps
        self._interface_runner: NamedInterfaceRunner = NamedInterfaceRunner('_main')
        self._is_init: bool = False
        self._is_pygame_init: bool = False
        if quit:
            self._interface_runner.register_event(quit_pygame, pg.QUIT)

    def is_init(self) -> bool:

        return self._is_init

    def init(self) -> None:

        self._interface_runner.init()
        self._is_init = True

    def register_event(
        self,
        func: FuncEvent,
        event_type: int,
        params: tuple[str, ...] = (),
        **kwargs: Any
    ) -> None:

        self._interface_runner.register_event(func, event_type, params, **kwargs)

    def event(
        self,
        event_type: int,
        params: tuple[str, ...] = (),
        **kwargs
    ) -> Callable[[FuncEvent], FuncEvent]:

        return self._interface_runner.event(event_type, params, **kwargs)

    def frame(self, func: FuncEvent) -> FuncEvent:

        return self._interface_runner.frame(func)

    def register_cls(self, cls: type[EventsClass]) -> type[EventsClass]:

        return self._interface_runner.register_cls(cls)

    def register_object(self, obj: object) -> None:

        self._interface_runner.register_object(obj)

    def register_grouped_cls(self, cls: type[EventsClass]) -> None:

        self._interface_runner.register_grouped_cls(cls)

    def run(self, screen: pg.Surface) -> None:
        """Executa o jogo.

        Somente as interfaces ativadas são executadas,
        sendo primeiro as de nível mais alto na hierarquia.

        Caso uma exceção ocorra, o pygame será fechado.
        O jogo pode ser fechado com ctrl+c
        de forma segura.
        """

        if not self._is_pygame_init:
            pg.init()
        try:
            self.init()
            self._run(screen)
        except QuitPygame: ...
        except KeyboardInterrupt:
            print()
        finally:
            pg.quit()

    def _run(self, screen: pg.Surface) -> None:
        """Executa o loop do jogo. """

        clock = pg.time.Clock()
        while True:
            for event in pg.event.get():
                self._interface_runner.run_event(event)
            self._interface_runner.run_frame(screen)

            clock.tick(self.fps)
            pg.display.flip()

    def __enter__(self) -> Self:

        pg.init()
        self._is_pygame_init = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:

        pg.quit()
        self._is_pygame_init = False

    def __repr__(self) -> str:
        return f'<Game({self.fps} fps)>'
