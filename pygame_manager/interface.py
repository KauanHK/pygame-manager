import pygame as pg
from .event import LoadingEvent, Event
from .exceptions import (
    SwitchInterface, ActivatedInterfaceError, DeactivatedInterfaceError, InterfaceExistsError, InterfaceNotFoundError
)
from .types import FuncEvent, FuncFrame, EventsClass
from functools import wraps
from abc import ABC, abstractmethod
from typing import Callable, Self, Any


class Manager(ABC):

    def __init__(self):
        self._interfaces: list[Interface] = []

    @property
    def active_interfaces(self) -> list[Self]:
        """As interfaces ativas."""
        return list(filter(lambda it: it.is_active, self._interfaces))

    @abstractmethod
    def add_event(self, func: FuncEvent, event_type: int, params: tuple[str, ...] = (), **kwargs) -> None: ...

    @abstractmethod
    def event(self, event_type: int, params: tuple[str, ...] = (), **kwargs) -> Callable[[FuncEvent], FuncEvent]: ...

    @abstractmethod
    def register_cls(self, cls: type) -> type: ...


class InterfaceManager(Manager):

    def __init__(self) -> None:
        """Base para interfaces. Gerencia eventos e frames."""

        super().__init__()

        # Registro de eventos
        self._owners: dict[str, list[LoadingEvent]] = {}
        self._classes: dict[str, type] = {}
        self._objects: dict[str, list[object]] = {}

        # Eventos finais (carregados)
        self._events: dict[int, list[Event]] = {}

        # Frame da interface
        self._frame = None

        self._init: bool = False

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

    def add_event(self, func: FuncEvent, event_type: int, params: tuple[str, ...] = (), **kwargs: Any) -> None:
        """Adiciona um evento para a lista de eventos.

        :param FuncEvent func: A função a ser adicionada.
        :param int event_type: O tipo do evento pygame.
        :param tuple params: Os parâmetros que devem ser passados ao chamar a função.
        :param Any kwargs: O valor do(s) atributos do evento pygame.
        """

        event = LoadingEvent(func, event_type, params, **kwargs)
        owner = '.'.join(func.__qualname__.split('.')[:-1])
        if owner not in self._owners:
            self._owners[owner] = []
        self._owners[owner].append(event)

    def event(self, event_type: int, params: tuple[str, ...] = (), **kwargs) -> Callable[[FuncEvent], FuncEvent]:
        """Registra uma função ou método.
        Se for um método, é necessário registrar a classe em que está inserido.

        A função/método será chamado durante a execução do jogo
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

        def decorator(f: FuncEvent) -> FuncEvent:
            self.add_event(f, event_type, params, **kwargs)
            return f

        return decorator

    def register_cls(self, cls: type[EventsClass]) -> type[EventsClass]:
        """Registra uma classe para carregar eventos dela.

        Necessário para registrar eventos como métodos e chamá-los passando
        a instância como primeiro parâmetro. Decora o seu __init__ para
        registrar todas as instâncias criadas.

        :param type cls: A classe a ser registrada.
        :return: A própria classe.
        """

        self.set_cls(cls)

        original_init = cls.__init__

        @wraps(original_init)
        def __init__(*args, **kwargs) -> None:
            original_init(*args, **kwargs)
            self.add_object(args[0])

        cls.__init__ = __init__
        return cls

    def frame(self, func: FuncFrame) -> FuncFrame:
        """Registra um frame para a interface.

        :param FuncFrame func: A função do frame.
        :return FuncFrame: A própria função do frame.
        """
        self._frame = func
        return func

    def run_event(self, pygame_event: pg.event.Event) -> None:
        """Executa um evento pygame e faz a troca de interfaces.

        :param pygame_event: O evento pygame.
        :return: None.
        """
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
        """Executa um evento pygame.
        
        :param pygame_event: O evento pygame.
        :return: None.
        """

        activated = self.active_interfaces
        for event in self._events.get(pygame_event.type, []):
            event.run(pygame_event)
        for it in activated:
            it.run_event(pygame_event)

    def _run_frame(self, screen: pg.Surface) -> None:
        """Executa o frame da interface e o das subinterfaces ativas. Primeiro,
        é executado seu frame e depois o das subinterfaces ativas.

        :param pg.Surface screen: A tela onde será desenhado o frame.
        """

        if self._frame is not None:
            self._frame(screen)
        for it in self.active_interfaces:
            it._run_frame(screen)

    def set_cls(self, cls: type[EventsClass]) -> None:
        """Registra uma classe para carregar seus eventos e retorna None.

        A diferença para register_cls() é que o __init__ da classe não é decorado,
        portanto não garante que os eventos de instâncias dessa classe sejam carregados.
        Use set_cls para registrar classes com eventos em múltiplas interfaces, ou
        use o decorador Group.register_cls().

        :param cls: A classe a ser registrada.
        :return: None.
        """
        self._classes[cls.__qualname__] = cls
        self._objects[cls.__qualname__] = []

    def add_object(self, obj: object) -> None:
        """Adiciona um objeto a lista de objetos de sua classe.

        É necessário registrar a classe antes de adicionar o
        objeto, caso contrário, lança um KeyError.
        Ao registrar um objeto, seus eventos serão executados.
        Para adicionar todos os objetos automaticamente, use
        o decorador Interface.register_cls() ou Group.register_cls().

        :param obj: O objeto a ser adicionado.
        """
        self._objects[obj.__class__.__qualname__].append(obj)


    def __enter__(self) -> Self:
        pg.init()
        self._init = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pg.quit()
        self._init = False


class Interface(InterfaceManager):
    objects: dict[str, Self] = {}

    def __init__(self, name: str) -> None:
        """Cria uma instância de Interface.
        
        :param str name: O nome da interface.
        """

        super().__init__()

        # Armazenar a instância no map objects
        if name in Interface.objects:
            raise InterfaceExistsError(f"Interface '{name}' já existe.")

        self._name = name
        Interface.objects[name] = self

        # Status da interface para indicar se é para ela ser executada ou não
        self._is_activated: bool = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_active(self) -> bool:
        return self._is_activated

    def activate(self) -> None:
        if self._is_activated:
            raise ActivatedInterfaceError(f'Interface {self.name} já está ativa.')
        self._is_activated = True

    def deactivate(self) -> None:
        if not self._is_activated:
            raise DeactivatedInterfaceError(f'Interface {self.name} já está desativada.')
        self._is_activated = False

    def register_interface(self, interface: Self) -> None:
        """Registra uma interface.

        :param Interface interface: A interface a ser registrada.
        :return: None.
        """

        self._interfaces.append(interface)

    def __repr__(self) -> str:
        return f'<Interface({self._name})>'


def get_interface(name: str) -> Interface:
    """Retorna a instância de Interface já criada com o nome fornecido.
    Se não houver nenhuma interface com o nome fornecido, lança um KeyError."""

    if name not in Interface.objects:
        raise InterfaceNotFoundError(f"Interface '{name}' não existe.")
    return Interface.objects[name]


def activate_interface(name: str) -> None:
    """Ativa a interface com o nome fornecido. Caso a interface já esteja ativa,
    lança um ActivatedInterfaceError.
    """
    get_interface(name).activate()


def deactivate_interface(name: str) -> None:
    """Desativa a interface com o nome fornecido. Caso a interface já esteja desativada,
    lança um DeactivatedInterfaceError.
    """
    get_interface(name).deactivate()
