import ctypes
import os
import sys
import time

from api import check_new_data
from config import config
from image.management import check_or_create_image_path
from logger import app_logger


def display_wallpapers() -> None:
    """
    A function that sets all files in a folder as wallpaper at equal intervals
    :return:
    """
    number_of_files = len(os.listdir(config.image_path))
    app_logger.info(f"Current number of images: {number_of_files}")

    change_wallpaper_interval = 1800 // number_of_files
    app_logger.info(f"Wallpapers will be changed every {change_wallpaper_interval} seconds")
    for file in os.listdir(config.image_path):
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.join(config.image_path, file), 1 | 2)
        app_logger.info("New wallpaper set up")
        time.sleep(change_wallpaper_interval)


def main():
    while True:  # Checks for new data every half hour
        check_or_create_image_path()
        check_new_data()
        display_wallpapers()


if __name__ == '__main__':
    app_logger.debug(f"App start with args: {sys.argv[1:]}")
    main()
