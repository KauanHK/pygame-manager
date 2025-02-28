import pygame as pg
from typing import Callable, TypeVar, Any


FuncEvent = TypeVar('FuncEvent', bound = Callable[..., Any])
FuncFrame = TypeVar('FuncFrame', bound = Callable[[pg.Surface], Any])
EventsClass = TypeVar('EventsClass', bound = type)
