import pygame as pg
from functools import wraps
from typing import Callable, Any


class BaseEvent:
    """Classe base para eventos."""

    def __init__(self, func: Callable, params: tuple[str, ...] = (), **kwargs) -> None:
        """
        :param Callable func: A função a ser chamada.
        :params tuple[str, ...] params: Tupla com os parâmetros a serem passados para a função.
        :param Any kwargs: Verificador do valor do(s) atributo(s) do evento pygame.
        """

        self.func = func
        self.params = params
        self.kwargs = kwargs

class Event(BaseEvent):

    def __init__(self, func: Callable, params: tuple[str, ...] = (), **kwargs) -> None:
        super().__init__(func, params, **kwargs)

    def run(self, pygame_event: pg.event.Event) -> None:
        """Processa um evento pygame. 
        Caso corresponda às configurações do Event, a função é executada.

        :param pygame.event.Event pygame_event: Evento do pygame.
        """

        params = self._get_params(pygame_event)
        event_dict = pygame_event.dict
        for k,v in self.kwargs.items():

            if callable(v):
                v_params = self._get_v_params(event_dict[k])
                if not v(*v_params):
                    return

            elif v != event_dict[k]:
                return

        self.func(**params)

    def _get_params(self, pygame_event: pg.event.Event) -> dict[str, Any]:
        """Retorna um dicionário com os parâmetros a serem passados para a função."""
        
        params = {}
        for param in self.params:
            params[param] = pygame_event.dict[param]
        return params
    
    def _get_v_params(self, value: Any) -> tuple[Any] | tuple[object, Any]:
        """Retorna uma tupla com os parâmetros a serem passados para uma função passada nos kwargs do Event.
        
        Caso a função dessa instância seja um método, retorna uma tupla com o objeto e o valor, 
        senão apenas uma tupla com o valor.

        :param Any value: Valor de um atributo evento pygame.
        """

        if hasattr(self.func, '__self__'):
            return self.func.__self__, value
        return (value,)
    
    def __repr__(self) -> str:
        return f'Event({self.func.__qualname__}{self.params}, kwargs = {self.kwargs})'


class LoadingEvent(BaseEvent):

    def __init__(self, func: Callable, event_type: int, params: tuple[str, ...] = (), **kwargs) -> None:
        """
        :param Callable func: A função a ser chamada.
        :param event_type: tipo do evento pygame.
        :params tuple[str, ...] params: Tupla com os parâmetros a serem passados para a função.
        :param Any kwargs: Verificador do valor do(s) atributo(s) do evento pygame.
        """

        super().__init__(func, params, **kwargs)
        self.event_type = event_type

    def load(self, cls: type | None = None, objects: list[object] | None = None) -> list[Event]:
        """Carrega o evento e retorna uma lista de Event's.
        
        Caso *objects* seja passado, criará os eventos com os boundmethods, retornando uma 
        lista de Event's, cada Event correspondendo a um boundmethod. Caso seja uma lista vazia, 
        retornará uma lista vazia.
        
        Caso *objects* seja None, retorna uma lista com um único Event com a função carregada.

        :param list[object] objects: lista com os objetos.
        """

        if cls is None:
            return [Event(self.func, self.params, **self.kwargs)]
        
        events = []
        for obj in objects:
            events.append(Event(getattr(obj, self.func.__name__), self.params, **self.kwargs))
        return events


class Events:

    def __init__(self) -> None:
        """Cria uma instância de Events.

        Registra, carrega e processa eventos pygame.
        """

        self._owners: dict[str, list[LoadingEvent]] = {}
        self._classes: dict[str, type] = {}
        self._objects: dict[str, list[object]] = {}
        self._events: dict[int, list[Event]] = {}

    def add(self, func: Callable, event_type: int, params: tuple[str, ...] = (), **kwargs) -> None:
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
        """

        event = LoadingEvent(func, event_type, params, **kwargs)
        owner = '.'.join(func.__qualname__.split('.')[:-1])
        if owner not in self._owners:
            self._owners[owner] = []
        self._owners[owner].append(event)

    def register_cls(self, cls: type) -> None:
        """Registra uma classe para carregar eventos de instâncias dessa classe."""

        self._classes[cls.__qualname__] = cls
        self._objects[cls.__qualname__] = []

        original_init = cls.__init__
        @wraps(original_init)
        def __init__(*args, **kwargs) -> None:
            original_init(*args, **kwargs)
            self._objects[cls.__qualname__].append(args[0])

        cls.__init__ = __init__

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
        
    def run(self, pygame_event: pg.event.Event) -> None:
        """Processa os eventos carregados.
        
        :param pygame.event.Event pygame_event: O evento pygame.
        """

        for event in self._events.get(pygame_event.type, []):
            event.run(pygame_event)

    def __repr__(self) -> str:
        return repr(self._events)
