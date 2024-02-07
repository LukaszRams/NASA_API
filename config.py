from __future__ import annotations

import os.path
import ctypes
import functools

from logger import app_logger
from typing import Callable, Any


setter_types = Callable[[Any, tuple[int, int] | str], None]


def safe_setter(func: setter_types) -> setter_types:
    """
    Decorator for setter property to catch and log raised errors
    """
    @functools.wraps(func)
    def wrapper(self: Any, value: tuple[int, int] | str) -> None:
        try:
            return func(self, value)
        except Exception as exception:
            app_logger.critical(exception)
            if self.__annotations__.get(func.__name__) == "str":
                value = ""
            else:
                value = (0, 0)
            self.__setattr__(f"_{func.__name__}", value)
    return wrapper


class ConfigMeta(type):
    """
    The Singleton class for config
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        app_logger.debug("ConfigMeta __call__ called")
        if cls not in cls._instances:
            app_logger.debug(f"{cls.__name__} already exists")
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Config(metaclass=ConfigMeta):
    """
    Global app config
    """
    resolution: tuple[int, int]
    image_path: str

    def __init__(self):
        """
        Init basic settings
        """
        self.resolution = self.get_screen_resolution()
        self.image_path = self.get_image_path()
        app_logger.info(f"Image path: {self.image_path}")
        app_logger.info(f"screen resolution: {self.resolution}")

    @property
    def resolution(self) -> tuple[int, int]:
        return self._resolution

    @resolution.setter
    @safe_setter
    def resolution(self, value: tuple[int, int]) -> None:
        match value:
            case (int(), int()) if isinstance(value, tuple):
                self._resolution = value
            case _:
                raise ValueError(f"Screen resolution should be of type tuple[int, int], current {type(value)}")

    @property
    def image_path(self) -> str:
        return self._image_path

    @image_path.setter
    @safe_setter
    def image_path(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError(f"image_path should be of type str, current {type(value)}")
        self._image_path = value

    @staticmethod
    def get_screen_resolution() -> tuple[int, int]:
        """
        Checks the resolution of the monitor and saves it
        :return: None
        """
        user32 = ctypes.windll.user32
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    @staticmethod
    def get_image_path() -> str:
        """
        Construct path to image folder
        :return: path to folder
        """
        return os.path.join(os.getcwd(), "images")


config = Config()
