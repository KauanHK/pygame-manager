import pygame as pg
from .interface import BaseInterface, Interface
from .utils import PygameInit, QuitPygame


class Game(BaseInterface):

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

    def register_interface(self, interface: Interface) -> None:
        """Registra uma interface."""

        self._interfaces.append(interface)

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
            self._run(screen)
        except QuitPygame: ...
        except KeyboardInterrupt:
            print()
        finally:
            pg.quit()

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
            for event in pg.event.get():
                self.run_event(event)
            self._run_frame(screen)

            clock.tick(60)
            pg.display.flip()

    def __repr__(self) -> str:
        return f'Interface({self._name})'
    