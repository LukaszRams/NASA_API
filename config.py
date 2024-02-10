"""
Configuration
"""

from __future__ import annotations

import ctypes
import functools
import os.path
from typing import Any, Callable, Type

from logger import app_logger

SetterType = Callable[[Any, tuple[int, int] | str], None]


def safe_setter(func: SetterType) -> SetterType:
    """
    Decorator for setter property to catch and log raised errors
    """

    @functools.wraps(func)
    def wrapper(self: Any, value: tuple[int, int] | str) -> None:
        try:
            func(self, value)
        except ValueError as exception:
            app_logger.critical(exception)
            if self.__annotations__.get(f"{func.__name__}_type") == "str":
                value = ""
            else:
                value = (0, 0)
            setattr(self, f"_{func.__name__}", value)

    return wrapper


class ConfigMeta(type):
    """
    The Singleton class for config
    """

    _instances: dict[Type[Any], Any] = {}

    def __call__(cls, *args: list[Any], **kwargs: dict[Any, Any]) -> Any:
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

    resolution_type: tuple[int, int]
    image_path_type: str

    def __init__(self) -> None:
        """
        Init basic settings
        """
        self.resolution = self.get_screen_resolution()
        self.image_path = self.get_image_path()
        app_logger.info(f"Image path: {self.image_path}")
        app_logger.info(f"screen resolution: {self.resolution}")

    @property
    def resolution(self) -> tuple[int, int]:
        """
        Property for desktop resolution
        :return: desktop resolution
        """
        return self._resolution

    @resolution.setter
    @safe_setter
    def resolution(self, value: tuple[int, int]) -> None:
        """
        Setter for resolution decorated by error logger
        :param value: value to be validated and set
        :return:
        """
        match value:
            case (int(), int()) if isinstance(value, tuple):
                self._resolution = value
            case _:
                raise ValueError(f"Screen resolution should be of type tuple[int, int], current {type(value)}")

    @property
    def image_path(self) -> str:
        """
        Property for image_path
        :return: path to folder with images
        """
        return self._image_path

    @image_path.setter
    @safe_setter
    def image_path(self, value: str) -> None:
        """
        Setter for image_path decorated by error logger
        :param value: value to set
        :return:
        """
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
