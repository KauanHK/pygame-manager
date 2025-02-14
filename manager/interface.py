import pygame as pg
from .event import LoadingEvent, Event
from functools import wraps
from typing import Callable, Self


class BaseInterface:

    def __init__(self) -> None:
        """Base para Interface."""

        # Registro de eventos
        self._owners: dict[str, list[LoadingEvent]] = {}
        self._classes: dict[str, type] = {}
        self._objects: dict[str, list[object]] = {}

        # Eventos finais (carregados)
        self._events: dict[int, list[Event]] = {}

        self._frame = None
        self._event_types: set[int] = set()

    def init(self) -> None:
        """Carrega os eventos registrados."""

        self._events: dict[int, list[Event]] = {}
        for owner, loading_events in self._owners.items():
            for le in loading_events:

                if le.event_type not in self._events:
                    self._events[le.event_type] = []

                cls = self._classes.get(owner)
                objects = self._objects.get(owner)
                events = le.load(cls, objects)
                self._events[le.event_type].extend(events)

    def get_event_types(self) -> tuple[int]:
        """Retorna uma tupla sem valores repetidos com os tipos dos eventos registrados, 
        mesmo que os eventos não tenham sido inicializados ainda."""
        return tuple(self._event_types)

    def event(self, event_type: int, params: tuple[str, ...] = (), **kwargs) -> Callable[[Callable], Callable]:
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
            self._events.add(f, event_type, params, **kwargs)
            self._event_types.add(event_type)
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

    def run_event(self, pygame_event: pg.event.Event) -> None:
        """Processa os eventos carregados.
        
        :param pygame.event.Event pygame_event: O evento pygame.
        """

        for event in self._events.get(pygame_event.type, []):
            event.run(pygame_event)


class Interface(BaseInterface):

    objects: dict[str, Self] = {}

    def __init__(self, name: str) -> None:
        """Cria uma instância de Interface.
        
        :param str name: O nome da interface.
        """

        super().__init__()
        self._name = name
        Interface.objects[name] = self

    def get_name(self) -> str:
        """Retorna o nome da interface."""
        return self._name

    def __repr__(self) -> str:
        return f'Interface({self._name})'


def get_interface(name: str) -> Interface:
    """Retorna a instância de Interface já criada com o nome fornecido.
    Se não houver nenhuma interface com o nome fornecido, lança um KeyError."""

    if name not in Interface.objects:
        raise KeyError(f"Interface '{name}' não existe.")
    return Interface.objects[name]
