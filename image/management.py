"""
File management
"""

import datetime
import os
import shutil

from config import config
from image.validators import validate_file
from logger import app_logger


def check_or_create_image_path() -> None:
    """
    Checks if the folder for graphics exists if not creates it
    :return: None
    """
    if not os.path.exists(config.image_path):
        os.makedirs(config.image_path)
        app_logger.debug("Image path created")
    app_logger.info("Image path exist")


def check_wallpapers() -> tuple[str | None, list[str], list[str]]:
    """
    Retrieves the date of the latest image from the folder, if the date is newer than the current date, forces a new
    image to be downloaded and returns error information about the folder
    :return: latest, valid, invalid
    """
    files = os.listdir(config.image_path)
    app_logger.info(f"Files in folder: {files}")

    # validated files
    valid = []
    invalid = []

    for file in files:
        if validate_file(file):
            valid.append(file)
            continue
        invalid.append(file)
    app_logger.debug(f"Number of valid/invalid files: {len(valid)}/{len(invalid)}")
    return max(valid) if valid else None, valid, invalid


def generate_code(date: str) -> str:
    """
    Concatenates a date into a string
    :param date: the date the photo was taken e.g. 2024-02-08 00:03:42
    :return: code %Y%m%d%H%M%S
    """
    code = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    return code.strftime("%Y%m%d%H%M%S")


def delete_files(files: list[str]) -> None:
    """
    Deletes files from the wallpaper folder

    Function iterate over filenames given in parameter and removing it from image path
    :param files: list of filenames to be removed
    :return: None
    """
    for file in files:
        path = os.path.join(config.image_path, file)
        if os.path.isfile(path):
            os.remove(path)
            app_logger.debug(f"File {file} removed")
        else:
            shutil.rmtree(path, ignore_errors=True)
            app_logger.debug(f"Path {file} removed")
