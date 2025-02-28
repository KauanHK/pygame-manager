from .interface import Interface, get_interface, Manager
from .utils import FuncEvent, EventsClass
from functools import wraps
from typing import Callable


def _multiple_interfaces_wrapper(func: FuncEvent) -> FuncEvent:
    """Decora eventos para que ele seja executado apenas nas interfaces ativas.

    :param FuncEvent func: A função do evento.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> None:
        if args[0].interface.is_active:
            func(*args, **kwargs)
    return wrapper


class Group(Manager):

    def __init__(self, *interfaces: Interface | str) -> None:
        """Agrupa interfaces para registrar eventos de maneira mais simples.

        :param interfaces: Interfaces a serem agrupadas.
        """
        super().__init__()
        for it in interfaces:
            if isinstance(it, str):
                it = get_interface(it)
            self._interfaces.append(it)

    def add(self, interface: Interface | str) -> None:
        """Adicionado uma interface ao grupo.

        :param interface: A interface ou seu nome.
        """

        if isinstance(interface, str):
            interface = get_interface(interface)
        self._interfaces.append(interface)

    def remove(self, interface: Interface | str) -> None:
        """Remove uma interface do grupo.

        :param interface: A interface ou seu nome.
        """

        if isinstance(interface, str):
            interface = get_interface(interface)
        self._interfaces.remove(interface)

    def add_event(self, func: FuncEvent, event_type: int, params: tuple[str, ...] = (), **kwargs) -> None:
        """Adiciona um evento para todas as interfaces do grupo e retorna None.

        :param func: A função do evento.
        :param event_type: O tipo do evento pygame.
        :param params: Os parâmetros de func.
        :param kwargs: As condições do evento.
        """

        for it in self._interfaces:
            it.add_event(func, event_type, params, **kwargs)

    def event(self, event_type: int, params: tuple[str, ...] = (), **kwargs) -> Callable[[FuncEvent], FuncEvent]:
        """Registra um evento para as interfaces do grupo.

        Adiciona o evento para todas as interfaces do grupo. O evento será executado
        até mesmo para interfaces registradas no grupo após o registro do evento.

        :param event_type: O tipo do evento pygame.
        :param params: Os parâmetros da função do evento.
        :param kwargs: As confições do evento.
        :return: O decorador para registrar a função.
        """
    
        def decorator(f: FuncEvent) -> FuncEvent:
            for it in self._interfaces:
                it.add_event(f, event_type, params, **kwargs)
            return _multiple_interfaces_wrapper(f)
        
        return decorator
    
    def register_cls(self, cls: type[EventsClass]) -> type[EventsClass]:
        """Registra uma classe para carregar seus eventos de métodos para todas as interfaces do grupo.

        :param cls: A classe a ser registrada.
        :return: A própria classe.
        """

        self._set_cls(cls)

        original_init = cls.__init__
        @wraps(original_init)
        def __init__(*args, **kwargs) -> None:
            original_init(*args, **kwargs)
            for it in self._interfaces:
                it.add_object(args[0])

        cls.__init__ = __init__
        return cls

    def _set_cls(self, cls: type[EventsClass]) -> None:
        """Adiciona uma classe para todas as interfaces do grupo
        sem decorar o seu .__init__() e retorna None.

        Ao registrar uma classe para uma interface,
        o .__init__() é decorado. Quando se registra uma classe
        para múltiplas interfaces, o .__init__() deve ser decorado apenas
        uma vez e apenas adicionar a classe a cada interface.

        :param cls: A classe a ser registrada.
        """

        for it in self._interfaces:
            it.set_cls(cls)

    def __repr__(self) -> str:
        return f'<Group({self._interfaces})>'
