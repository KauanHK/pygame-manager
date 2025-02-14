import pygame as pg
from typing import Callable, NoReturn


class QuitPygame(BaseException): ...

def quit_pygame(*args) -> NoReturn:
    raise QuitPygame(*args)

class PygameInit:

    def __enter__(self) -> None:
        pg.init()

    def __exit__(self, _, e, *args) -> None:

        if e:
            pg.quit()

class SwitchInterface(BaseException):

    def __init__(self, name: str) -> None:
        self.name = name


def switch_interface(name: str) -> Callable[[], NoReturn]:
    raise SwitchInterface(name)
