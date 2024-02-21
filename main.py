"""
Main file of the app
"""

import ctypes
import os
import sys
import time

from api import check_new_data
from config import config
from image.management import check_or_create_image_path, delete_files
from logger import app_logger


def display_wallpapers() -> None:
    """
    A function that sets all files in a folder as wallpaper at equal intervals
    :return:
    """
    number_of_files = len(os.listdir(config.image_path))
    app_logger.info(f"Current number of images: {number_of_files}")
    if number_of_files:
        change_wallpaper_interval = config.sync_interval // number_of_files
        app_logger.info(f"Wallpapers will be changed every {change_wallpaper_interval} seconds")
        for file in os.listdir(config.image_path):
            try:
                ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.join(config.image_path, file), 1 | 2)
            except OSError as exception:
                app_logger.critical(f"Exception while set wallpaper: {exception}")
                delete_files([file])
                continue
            app_logger.info("New wallpaper set up")
            time.sleep(change_wallpaper_interval)


def main() -> None:
    """
    Main loop of the program
    :return:
    """
    while True:  # Checks for new data every half hour
        check_or_create_image_path()
        check_new_data()
        display_wallpapers()


if __name__ == "__main__":
    app_logger.debug(f"App start with args: {sys.argv[1:]}")
    main()
