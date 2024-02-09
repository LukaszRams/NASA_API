import os
import threading

import requests

from config import config
from image.management import check_wallpapers, delete_files, generate_code
from image.processing import process_image
from logger import app_logger


def check_new_data() -> None:
    """
    Checks whether new data are available and, if available, triggers recording
    :return: None
    """
    # get last image
    try:
        app_logger.info("Connecting to API")
        request = requests.get("https://epic.gsfc.nasa.gov/api/natural")
        request.raise_for_status()
        request = request.json()

        app_logger.debug("Response parsed to json")

        last_record = request[-1]

        # generate code
        code = generate_code(last_record["date"])

        # check actual wallpapers
        latest, valid, invalid = check_wallpapers()

        # delete invalid files and folders
        delete_files(invalid)

        # check for new images
        if not latest or latest < code:

            # download the latest photos
            for record in request:
                start_thread(record)

            # delete old valid
            delete_files(valid)

        app_logger.info("Join working threads")
        for thread in threading.enumerate()[2:]:
            thread.join()
        app_logger.info("All threads joined")

    except requests.exceptions.ConnectionError as exception:
        app_logger.critical(f"Connection Error: {exception}")


def start_thread(record: dict[str, str | dict[str, str]]) -> None:
    """
    Collect data from API record, create and start thread
    :param record: record of the data from API
    :return: nothing
    """

    code = generate_code(record["date"])
    thread_name = f"Thread_{record["image"]}"
    kwargs = {
        "code": code,
        "image_name": record["image"]
    }
    # create Thread object
    thread = threading.Thread(target=download_and_save_image,
                              name=thread_name,
                              kwargs=kwargs,
                              daemon=True)
    app_logger.debug(f"New thread initialized with kwargs: {kwargs}")

    # start Thread object
    thread.start()


def download_and_save_image(code: str, image_name: str) -> None:
    """
    Downloads and saves an image in a folder
    Image name:
        YearMonthDayHourMinuteSecond
    Format:
        PNG
    :param code: Date and time of taking the picture recorded in a string
    :param image_name: Name of image in api
    :return: None
    """
    try:
        app_logger.debug("Connecting to image archive and downloading image")
        request = requests.get(
            f"https://epic.gsfc.nasa.gov/archive/natural/{code[0:4]}/{code[4:6]}/{code[6:8]}/png/{image_name}.png")
        if request.status_code == 200:
            # path to image
            app_logger.debug("Image downloaded")
            image_path = os.path.join(config.image_path, code + ".png")

            # save image
            app_logger.debug("Image saving")
            with open(image_path, "wb") as f:
                f.write(request.content)
            app_logger.debug("Image saved")

            # resize image
            app_logger.debug("Image processing")
            process_image(image_path, code)
            app_logger.debug("End of image processing")
    except requests.exceptions.ConnectionError as exception:
        app_logger.error(f"Unknown exception: {exception}")
