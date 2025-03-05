from ._interface import NamedInterfaceRunner
from .exceptions import InterfaceExistsError, InterfaceNotFoundError
from typing import Self


class Interface(NamedInterfaceRunner):

    objects: dict[str, Self] = {}

    def __init__(self, name: str) -> None:
        """Cria uma instância de Interface.
        
        :param str name: O nome da interface.
        """

        # Armazenar a instância no map objects
        if name in Interface.objects:
            raise InterfaceExistsError(f"Interface '{name}' já existe.")

        super().__init__(name)
        Interface.objects[name] = self

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
