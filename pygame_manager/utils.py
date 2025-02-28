from .exceptions import QuitPygame, SwitchInterface
from typing import NoReturn


def quit_pygame(*args) -> NoReturn:
    raise QuitPygame(*args)


def switch_interface(name: str) -> NoReturn:
    raise SwitchInterface(name)
