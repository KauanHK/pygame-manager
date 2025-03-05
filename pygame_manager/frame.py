import pygame as pg
from .types import FuncFrame
from typing import Any


class FrameManager:

    def __init__(self, func: FuncFrame | None = None, **kwargs: Any) -> None:

        self._func: FuncFrame | None = func
        self._kwargs: dict[str, Any] = kwargs

    def load(self, func: FuncFrame) -> FuncFrame:

        self._func = func
        return func

    def setup(self, **kwargs: Any) -> None:

        self._kwargs = kwargs

    def run(self, screen: pg.Surface) -> None:

        if self._func is not None:
            self._func(screen, **self._kwargs)
