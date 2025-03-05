import pygame as pg
from .types import EventsClass, FuncEvent
from functools import wraps
from typing import Callable, Any


def _get_owner_qualname(func: Callable) -> str:
    return '.'.join(func.__qualname__.split('.')[:-1])


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
        self.owner_qualname: str = _get_owner_qualname(func)


class Event(BaseEvent):

    def run(self, pygame_event: pg.event.Event) -> None:
        """Processa um evento pygame. 
        Caso corresponda às configurações do Event, a função é executada.

        :param pygame.event.Event pygame_event: Evento do pygame.
        """

        params = self._get_params(pygame_event)
        event_dict = pygame_event.dict
        for k, v in self.kwargs.items():

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


class EventsManager:

    def __init__(self) -> None:

        super().__init__()
        self._loading_events: dict[str, list[LoadingEvent]] = {}
        self._classes: dict[str, type[EventsClass]] = {}
        self._objects: dict[str, list[object]] = {}
        self._events: dict[int, list[Event]] = {}
        self._is_init: bool = False

    def is_init(self) -> bool:
        return self._is_init

    def init(self) -> None:

        self._events.clear()
        for owner in self._loading_events:
            for le in self._loading_events[owner]:
                cls = self._classes.get(le.owner_qualname)
                objects = self._objects.get(le.owner_qualname)
                self._events[le.event_type] = self._events.get(le.event_type, [])
                self._events[le.event_type].extend(le.load(cls, objects))
            
    def register_event(self, func: FuncEvent, event_type: int, params: tuple[str, ...] = (), **kwargs: Any) -> FuncEvent:

        le: LoadingEvent = LoadingEvent(func, event_type, params, **kwargs)
        self._loading_events.get(le.owner_qualname, []).append(le)
        return func

    def register_cls(self, cls: type[EventsClass]) -> type[EventsClass]:
        """Registra uma classe para carregar eventos dela.

        Necessário para registrar eventos como métodos e chamá-los passando
        a instância como primeiro parâmetro. Decora o seu __init__ para
        registrar todas as instâncias criadas.

        :param type cls: A classe a ser registrada.
        :return: A própria classe.
        """

        self.register_grouped_cls(cls)

        original_init = cls.__init__

        @wraps(original_init)
        def __init__(*args, **kwargs) -> None:
            original_init(*args, **kwargs)
            self.register_object(args[0])

        cls.__init__ = __init__
        return cls

    def register_object(self, obj: object) -> None:
        """Adiciona um objeto a lista de objetos de sua classe.

        É necessário registrar a classe antes de adicionar o
        objeto, caso contrário, lança um KeyError.
        Ao registrar um objeto, seus eventos serão executados.
        Para adicionar todos os objetos automaticamente, use
        o decorador Interface.register_cls() ou Group.register_cls().

        :param obj: O objeto a ser adicionado.
        """
        self._objects[obj.__class__.__qualname__].append(obj)

    def register_grouped_cls(self, cls: type[EventsClass]) -> None:
        """Registra uma classe para carregar seus eventos e retorna None.

        A diferença para register_cls() é que o __init__ da classe não é decorado,
        portanto não garante que os eventos de instâncias dessa classe sejam carregados.
        Use register_grouped_cls para registrar classes com eventos em múltiplas interfaces, ou
        use o decorador Group.register_cls().

        :param cls: A classe a ser registrada.
        :return: None.
        """
        self._classes[cls.__qualname__] = cls
        self._objects[cls.__qualname__] = []

    def run(self, pygame_event: pg.event.Event) -> None:

        for event in self._events.get(pygame_event.type, []):
            event.run(pygame_event)
