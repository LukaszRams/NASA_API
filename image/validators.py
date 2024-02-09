import os.path
from datetime import datetime
from PIL import Image
from config import config
from logger import app_logger


def check_file_extension(file: str) -> bool:
    """
    File should have .png extension
    :param file: filename
    :return: True if extension is correct else False
    """
    return file.endswith(".png")


def check_length_of_file(file: str) -> bool:
    """
    Check filename contains 18 characters

    Template of filename:
    YYYYmmddHHMMSS.png
    :param file: filename to checked
    :return: True if length is correct else False
    """
    return len(file) == 18


def check_filename_without_extension(file: str) -> bool:
    """
    Filename might be mapped to int
    :param file: filename
    :return: True if filename might be mapped else false
    """
    try:
        int(file[:14])
        return True
    except ValueError:
        return False


def check_date_of_image(file: str) -> bool:
    """
    Check if parsed date is greater than now
    :param file: filename
    :return: True if greater else False
    """
    pattern = datetime.now().strftime("%Y%m%d%H%M%S")
    return file[:14] > pattern


def check_if_file_is_not_broken(file: str) -> bool:
    """
    Check if file exists, open and size is equal to screen resolution
    :param file: filename
    :return: True if file passes tests else False
    """
    filepath = os.path.join(config.image_path, file)
    try:
        image = Image.open(filepath)
        image.verify()
        return image.size == config.resolution
    except (IOError, SyntaxError) as exception:
        app_logger.critical(f"Error while validation: {exception}")
        return False


def validate_file(file: str) -> bool:
    """
    Validate if file is correct
    :param file: filename
    :return: True if file is correct else False
    """
    validators = [
        check_file_extension,
        check_length_of_file,
        check_filename_without_extension,
        check_date_of_image,
        check_if_file_is_not_broken
    ]
    for validator in validators:
        if not validator(file):
            app_logger.info(f"Image error detected with validator: {validator.__name__} {validator.__doc__}")
            return False
    return True

