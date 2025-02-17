import pygame as pg
from .interface import BaseInterface, Interface
from .event import Event, LoadingEvent
from .utils import PygameInit, QuitPygame, SwitchInterface, FuncEvent
from functools import wraps
from typing import Callable


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

    def event(self, event_type: int, params: tuple[str, ...] = (), **kwargs) -> Callable[[FuncEvent], FuncEvent]:
        """Registra uma função ou método. 
        Se for um método, é necessário registrar a classe em que está inserido.

        A função/método será chamada durante a execução do jogo 
        quando houver um evento pygame do tipo *event_type* 
        e as condições passadas em *kwargs* forem verdadeiras, 
        passando os parâmetros especificados em *params*.

        :param int event_type:
            O tipo do evento pygame.

        :param tuple, Opcional params:
            Tupla de strings com os parâmetros que serão passados para a função.

        :param Any, Opcional kwargs:
            Os atributos do evento pygame. Usado para verificar se o valor do(s) 
            atributo(s) do evento são iguais aos especificados.

        Exemplos
        --------

            ```python
            @interface.event(pygame.MOUSEBUTTONDOWN, params = ('pos', 'button'))
            def click(pos, button):
                if button == pygame.BUTTON_LEFT and button_rect.collidepoint(pos):
                    switch_interface('game')

            @interface.event(
                pygame.MOUSEBUTTONDOWN,
                button = pygame.BUTTON_LEFT,
                pos = lambda pos: button_rect.collidepoint(pos)
            )
            def click():
                switch_interface('game')

            @interface.register_cls
            class Button:
                ...
                @interface.event(
                    pygame.MOUSEBUTTONDOWN,
                    button = pygame.BUTTON_LEFT,
                    pos = lambda self, pos: button_rect.collidepoint(pos)
                )
                def click(self):
                    switch_interface('game')
            ```
        """

        def decorator(f: Callable) -> Callable:
            event = LoadingEvent(f, event_type, params, **kwargs)
            owner = '.'.join(f.__qualname__.split('.')[:-1])
            if owner not in self._owners:
                self._owners[owner] = []
            self._owners[owner].append(event)
            return f

        return decorator
    
    def register_cls(self, cls: type) -> type:
        """Registra uma classe para carregar eventos de instâncias dessa classe."""
        
        self._classes[cls.__qualname__] = cls
        self._objects[cls.__qualname__] = []

        original_init = cls.__init__
        @wraps(original_init)
        def __init__(*args, **kwargs) -> None:
            original_init(*args, **kwargs)
            self._objects[cls.__qualname__].append(args[0])

        cls.__init__ = __init__
        return cls
    
    def frame(self, frame: Callable) -> None:
        """Registra um frame para a interface."""
        self._frame = frame

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

    def run_event(self, pygame_event: pg.event.Event) -> None:

        try:
            self._run_event(pygame_event)
        except SwitchInterface as e:
            activated = False
            for it in self._interfaces:
                if it.get_name() == e.name:
                    it.activate()
                    activated = True
                else:
                    it.deactivate()
            if not activated:
                raise e

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

    def _run_event(self, pygame_event: pg.event.Event) -> None:
        """Processa os eventos carregados.
        
        :param pygame.event.Event pygame_event: O evento pygame.
        """

        activated = self.get_activated()
        for event in self._events.get(pygame_event.type, []):
            event.run(pygame_event)
        for it in activated:
            it.run_event(pygame_event)

    def _run_frame(self, screen: pg.Surface) -> None:
        """Executa um frame, primeiro o frame global, se tiver, e o frame da interface."""

        if self._frame is not None:
            self._frame(screen)
        for it in self.get_activated():
            it._run_frame(screen)

    def __repr__(self) -> str:
        return f'Interface({self._name})'
    
