import pygame as pg
from .interface import BaseInterface, Interface, get_interface
from .utils import PygameInit, QuitPygame, SwitchInterface, quit_pygame


# Game herda BaseInterface, pois seu comportamento 
# é parecido com o de uma interface, uma vez que 
# também possui eventos e frame, que no caso, são globais.
class Game(BaseInterface):

    def __init__(self, quit: bool = True) -> None:
        """Gerenciador do jogo.

        :param quit: Se True, registra um evento de pygame.QUIT para fechar o jogo.
        """
        
        super().__init__()
        self._interfaces: list[Interface] = []
        self._current_interface: Interface | None = None
        self._current_event_types: tuple[int, ...]
        self._init = False

        if quit:
            self._events.add(quit_pygame, pg.QUIT)
            self._event_types.add(pg.QUIT)

    def init(self) -> None:
        """Inicializa os eventos registrados."""

        super().init()
        for interface in self._interfaces:
            interface.init()

    def register_interface(self, interface: Interface) -> None:
        """Registra uma interface."""

        if self._current_interface is None:
            self._current_interface = interface
        self._interfaces.append(interface)

    def pygame_init(self) -> PygameInit:
        """Retorna um context manager para inicialização segura do pygame.
        O context manager inicializa o pygame e só o fecha se uma exceção ocorrer.

        Use dentro de um bloco with:
        ```python
        with game.pygame_init():
            import main_menu, options_menu, game
        ```
        """

        self._init = True
        return PygameInit()

    def run(self, screen: pg.Surface) -> None:
        """Executa o jogo.
        
        Caso uma exceção ocorra, o pygame será fechado. 
        Isso significa que o jogo pode ser fechado com ctrl+c
        de forma segura.
        """

        if not self._init:
            pg.init()
        try:
            self.init()
            self._current_event_types = self.get_event_types()
            self._run(screen)
        except QuitPygame: ...
        except KeyboardInterrupt:
            print()
        finally:
            pg.quit()

    def get_event_types(self) -> tuple[str, ...]:
        """Retorna uma tupla com os tipos dos eventos globais e da interface atual (nenhum duplicado)."""
        return tuple((*self._event_types, *self._current_interface.get_event_types()))
    
    def _run(self, screen: pg.Surface) -> None:
        """Executa o loop do jogo."""

        # 1. Executa os eventos
          # Primeiro os eventos globais, depois os da interface atual
        # 2. Executa o frame
          # Primeiro o frame global, depois os da interface atual
        # Caso ocorra uma exceção de SwitchInterface
          # Atualiza a interface atual
          # Atualiza os event_types

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
        """Executa os eventos, primeiro os globais, depois os da interface atual."""

        for pygame_event in pg.event.get(self._current_event_types):
            self.run_event(pygame_event)
            self._current_interface.run_event(pygame_event)

    def _run_frame(self, screen: pg.Surface) -> None:
        """Executa um frame, primeiro o frame global, se tiver, e o frame da interface."""

        if self._frame is not None:
            self._frame(screen)
        self._current_interface.run_frame(screen)
