import pygame as pg
from .interface import InterfaceManager, Interface
from .utils import PygameInit, QuitPygame, quit_pygame


class Game(InterfaceManager):

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
        if quit:
            self.event(pg.QUIT)(quit_pygame)

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
        
        Somente as interfaces ativadas são executadas, 
        sendo primeiro as de nível mais alto na hierarquia.
        
        Caso uma exceção ocorra, o pygame será fechado. 
        O jogo pode ser fechado com ctrl+c
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
        """Executa o loop do jogo. """

        clock = pg.time.Clock()
        while True:
            for event in pg.event.get():
                self.run_event(event)
            self._run_frame(screen)

            clock.tick(self.fps)
            pg.display.flip()

    def __repr__(self) -> str:
        return f'Interface({self._name})'
    