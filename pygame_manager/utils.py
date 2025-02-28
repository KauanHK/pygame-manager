import pygame as pg
from typing import Callable, NoReturn, TypeVar, Any


FuncEvent = TypeVar('FuncEvent', bound = Callable[..., Any])
FuncFrame = TypeVar('FuncFrame', bound = Callable[[pg.Surface], Any])
EventsClass = TypeVar('EventsClass', bound = type)

class QuitPygame(BaseException): ...

def quit_pygame(*args) -> NoReturn:
    raise QuitPygame(*args)

class SwitchInterface(BaseException):

    def __init__(self, name: str) -> None:
        self.name = name


def switch_interface(name: str) -> Callable[[], NoReturn]:
    raise SwitchInterface(name)


class ActivatedInterfaceError(BaseException): ...
class DeactivatedInterfaceError(BaseException): ...
