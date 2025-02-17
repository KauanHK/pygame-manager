import pygame as pg
from .event import LoadingEvent, Event
from .utils import SwitchInterface, FuncEvent
from functools import wraps
from abc import ABC, abstractmethod
from typing import Callable, Self


class Base(ABC):

    def get_activated(self) -> list[Self]:
        return list(filter(lambda it: it.is_activated(), self._interfaces))

    @abstractmethod
    def add_event(self, func: FuncEvent, event_type: int, params: tuple[str, ...] = (), **kwargs) -> None: ...

    @abstractmethod
    def event(self, event_type: int, params: tuple[str, ...] = (), **kwargs) -> Callable[[FuncEvent], FuncEvent]: ...

    @abstractmethod
    def register_cls(self, cls: type) -> type: ...


class BaseInterface(Base):

    def __init__(self) -> None:

        # Registro de eventos
        self._owners: dict[str, list[LoadingEvent]] = {}
        self._classes: dict[str, type] = {}
        self._objects: dict[str, list[object]] = {}

        # Eventos finais (carregados)
        self._events: dict[int, list[Event]] = {}

        # Subinterfaces registradas
        self._interfaces: list[Interface] = []

        # Frame da interface
        self._frame = None

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
        
        for it in self._interfaces:
            it.init()

    def add_event(self, func: FuncEvent, event_type: int, params: tuple[str, ...] = (), **kwargs) -> None:

        event = LoadingEvent(func, event_type, params, **kwargs)
        owner = '.'.join(func.__qualname__.split('.')[:-1])
        if owner not in self._owners:
            self._owners[owner] = []
        self._owners[owner].append(event)

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

        def decorator(f: FuncEvent) -> FuncEvent:
            self.add_event(f, event_type, params, **kwargs)
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

        try:
            self._run_event(pygame_event)
        except SwitchInterface as e:
            activated = False
            for it in self._interfaces:
                if it.name == e.name:
                    it.activate()
                    activated = True
                else:
                    it.deactivate()
            if not activated:
                raise e
            
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



class Interface(BaseInterface):

    objects: dict[str, Self] = {}

    def __init__(self, name: str) -> None:
        """Cria uma instância de Interface.
        
        :param str name: O nome da interface.
        """

        super().__init__()

        # Armazenar a instância no map objects
        self._name = name
        Interface.objects[name] = self

        # Status da interface para indicar se é para ela ser executada ou não
        self._is_activated: bool = False

    @property
    def name(self) -> str:
        return self._name

    def is_activated(self) -> bool:
        return self._is_activated

    def activate(self) -> None:
        self._is_activated = True

    def deactivate(self) -> None:
        self._is_activated = False

    def register_subinterface(self, interface: Self) -> None:
        """Registra uma interface."""

        self._interfaces.append(interface)

    def __repr__(self) -> str:
        return f'Interface({self._name})'


def get_interface(name: str) -> Interface:
    """Retorna a instância de Interface já criada com o nome fornecido.
    Se não houver nenhuma interface com o nome fornecido, lança um KeyError."""

    if name not in Interface.objects:
        raise KeyError(f"Interface '{name}' não existe.")
    return Interface.objects[name]

def activate_interface(name: str) -> None:
    get_interface(name).activate()

def deactivate_interface(name: str) -> None:
    get_interface(name).deactivate()
