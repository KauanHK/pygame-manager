import pygame as pg
from .event import EventsManager
from .frame import FrameManager
from .types import FuncEvent, EventsClass, FuncFrame
from .exceptions import ActivatedInterfaceError, DeactivatedInterfaceError, SwitchInterface
from abc import ABC, abstractmethod
from typing import Any, Callable, Self


class BaseInterface(ABC):

    @abstractmethod
    def init(self): ...

    @abstractmethod
    def register_event(
        self,
        func: FuncEvent,
        event_type: int,
        params: tuple[str, ...] = (),
        **kwargs: Any
    ) -> None: ...

    @abstractmethod
    def event(
        self,
        event_type: int,
        params: tuple[str, ...] = (),
        **kwargs
    ) -> Callable[[FuncEvent], FuncEvent]: ...

    @abstractmethod
    def frame(self, func: FuncEvent) -> FuncEvent: ...

    @abstractmethod
    def register_cls(self, cls: type[EventsClass]) -> type[EventsClass]: ...

    @abstractmethod
    def register_object(self, obj: object) -> EventsClass: ...

    @abstractmethod
    def register_grouped_cls(self, cls: type[EventsClass]) -> None: ...


class InterfaceLoader(BaseInterface, ABC):

    def __init__(self) -> None:
        self.interfaces: list[Self] = []

    def register_interface(self, interface: Self) -> None:
        """Registra uma interface.

        :param Interface interface: A interface a ser registrada.
        :return: None.
        """

        self.interfaces.append(interface)

    def remove_interface(self, interface: Self) -> None:

        self.interfaces.remove(interface)


class InterfaceRunner(InterfaceLoader, ABC):

    def __init__(self) -> None:

        super().__init__()
        self._events: EventsManager = EventsManager()
        self._frame: FrameManager = FrameManager()

    @abstractmethod
    def run_event(self, pygame_event: pg.event.Event) -> None: ...

    @abstractmethod
    def run_frame(self, screen: pg.Surface) -> None: ...

    def init(self) -> None:
        """Carrega os eventos registrados."""

        self._events.init()
        for it in self.interfaces:
            it.init()

    def register_event(
            self,
            func: FuncEvent,
            event_type: int,
            params: tuple[str, ...] = (),
            **kwargs: Any
    ) -> FuncEvent:
        """Adiciona um evento para a lista de eventos.

        :param FuncEvent func: A função a ser adicionada.
        :param int event_type: O tipo do evento pygame.
        :param tuple params: Os parâmetros que devem ser passados ao chamar a função.
        :param Any kwargs: O valor do(s) atributos do evento pygame.
        """

        return self._events.register_event(func, event_type, params, **kwargs)

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
            return self._events.register_event(f, event_type, params, **kwargs)
        return decorator

    def frame(self, func: FuncFrame) -> FuncFrame:
        """Registra um frame para a interface.

        :param FuncFrame func: A função do frame.
        :return FuncFrame: A própria função do frame.
        """

        return self._frame.load(func)

    def register_cls(self, cls: type[EventsClass]) -> type[EventsClass]:
        """Registra uma classe para carregar eventos dela.

        Necessário para registrar eventos como métodos e chamá-los passando
        a instância como primeiro parâmetro. Decora o seu __init__ para
        registrar todas as instâncias criadas.

        :param type cls: A classe a ser registrada.
        :return: A própria classe.
        """

        return self._events.register_cls(cls)

    def register_object(self, obj: object) -> None:
        """Adiciona um objeto a lista de objetos de sua classe.

        É necessário registrar a classe antes de adicionar o
        objeto, caso contrário, lança um KeyError.
        Ao registrar um objeto, seus eventos serão executados.
        Para adicionar todos os objetos automaticamente, use
        o decorador Interface.register_cls() ou Group.register_cls().

        :param obj: O objeto a ser adicionado.
        """

        self._events.register_object(obj)

    def register_grouped_cls(self, cls: type[EventsClass]) -> None:
        """Registra uma classe para carregar seus eventos e retorna None.

        A diferença para register_cls() é que o __init__ da classe não é decorado,
        portanto não garante que os eventos de instâncias dessa classe sejam carregados.
        Use register_grouped_cls para registrar classes com eventos em múltiplas interfaces, ou
        use o decorador Group.register_cls().

        :param cls: A classe a ser registrada.
        :return: None.
        """

        self._events.register_grouped_cls(cls)


class NamedInterface(InterfaceRunner):

    def __init__(self, name: str) -> None:

        super().__init__()
        self._name: str = name
        self._is_active: bool = False

    @property
    def name(self) -> str:
        return self._name

    def is_active(self) -> bool:

        return self._is_active

    def get_active_interfaces(self) -> list[Self]:

        return list(filter(lambda it: it.is_active(), self.interfaces))

    def activate(self) -> None:

        if self._is_active:
            raise ActivatedInterfaceError(f'Interface {self.name} já está ativa.')
        self._is_active = True

    def deactivate(self) -> None:

        if not self._is_active:
            raise DeactivatedInterfaceError(f'Interface {self.name} já está desativada.')
        self._is_active = False


class NamedInterfaceRunner(NamedInterface):

    def run_event(self, pygame_event: pg.event.Event) -> None:
        """Executa um evento pygame e faz a troca de interfaces.

        :param pygame_event: O evento pygame.
        :return: None.
        """
        try:
            self._run_event(pygame_event)
        except SwitchInterface as e:
            activated = False
            for it in self.interfaces:
                if it.name == e.name:
                    it.activate()
                    activated = True
                else:
                    it.deactivate()
            if not activated:
                raise e

    def run_frame(self, screen: pg.Surface) -> None:
        """Executa o frame da interface e o das subinterfaces ativas. Primeiro,
        é executado seu frame e depois o das subinterfaces ativas.

        :param pg.Surface screen: A tela onde será desenhado o frame.
        """

        self._frame.run(screen)
        for it in self.get_active_interfaces():
            it.run_frame(screen)

    def _run_event(self, pygame_event: pg.event.Event) -> None:
        """Executa um evento pygame.

        :param pygame_event: O evento pygame.
        :return: None.
        """

        self._events.run(pygame_event)
        for it in self.get_active_interfaces():
            it.run_event(pygame_event)
