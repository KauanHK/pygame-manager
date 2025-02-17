import pygame as pg
from typing import Callable, NoReturn, TypeVar, Any


FuncEvent = TypeVar('FuncEvent', bound = Callable[..., Any])

class QuitPygame(BaseException): ...

def quit_pygame(*args) -> NoReturn:
    raise QuitPygame(*args)

class PygameInit:

    _init = False

    def __enter__(self) -> None:
        
        if not PygameInit._init:
            pg.init()
            PygameInit._init = True

    def __exit__(self, _, e, *args) -> None:

        if e:
            pg.quit()

class SwitchInterface(BaseException):

    def __init__(self, name: str) -> None:
        self.name = name


def switch_interface(name: str) -> Callable[[], NoReturn]:
    raise SwitchInterface(name)
