import requests
import ctypes
from PIL import Image, ImageDraw, ImageFont
import shutil
import os
from datetime import datetime
from typing import List, Tuple
import threading
import time
from config import config



def check_or_create_image_path() -> None:
    """
    Checks if the folder for graphics exists if not creates it
    :return: None
    """
    if not os.path.exists(config.config.image_path):
        os.makedirs(config.config.image_path)


def check_new_data() -> None:
    """
    Checks whether new data are available and, if available, triggers recording
    :return: None
    """

    # get last image
    try:
        request = requests.get("https://epic.gsfc.nasa.gov/api/natural")
        if request.status_code == 200:
            request = request.json()
            record = request[-1]

            # generate code
            code = generate_code(record["date"])

            # check actual wallpapers
            latest, valid, invalid = check_wallpapers()

            # delete invalid files and folders
            if invalid:
                delete_files(invalid)

            # check for new images
            if not latest or latest < code:

                # download the latest photos
                for dict_ in request:
                    code = generate_code(dict_["date"])

                    # create Thread object
                    download = Download(code, dict_["image"])

                    # start Thread object
                    download.start()

                # delete old valid
                if valid:
                    delete_files(valid)
    except requests.exceptions.ConnectionError:
        pass


def check_wallpapers() -> Tuple[str, List[str], List[str]]:
    """
    Retrieves the date of the latest image from the folder, if the date is newer than the current date, forces a new
    image to be downloaded and returns error information about the folder
    :return: latest, valid, invalid
    """
    files = os.listdir(config.config.image_path)

    # validate files
    invalid = []
    valid = []
    max_date = datetime.now()
    max_date = str(max_date.year) + \
               str(max_date.month) + \
               str(max_date.day) + \
               str(max_date.hour) + \
               str(max_date.minute) + \
               str(max_date.second)

    for file in files:
        # check extension
        if not file.endswith(".png"):
            invalid.append(file)
            continue

        # check len filename
        if not len(file) == 18:
            invalid.append(file)
            continue

        # check if filename might be mapped to integer
        try:
            int(file[:14])
        except ValueError:
            invalid.append(file)
            continue

        # validate date
        if file[:14] > max_date:
            invalid.append(file)
            continue

        # check file size
        if Image.open(os.path.join(config.image_path, file)).size != SCREEN:
            invalid.append(file)
            continue

        valid.append(file)

    return max(valid)[:-4] if valid else None, valid, invalid


def delete_files(files: List[str]) -> None:
    """
    Deletes files from the wallpaper folder
    :param files: Files to be removed
    :return: None
    """
    for file in files:
        path = os.path.join(config.image_path, file)
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path, ignore_errors=True)


def generate_code(date: str) -> str:
    """
    Concatenates a date into a string
    :param date: the date the photo was taken
    :return: code
    """
    code = date.split(" ")
    return "".join(e for e in code[0].split("-")) + "".join(e for e in code[1].split(":"))


def set_screen_resolution() -> None:
    """
    Checks the resolution of the monitor and saves it
    :return: None
    """
    user32 = ctypes.windll.user32
    global SCREEN
    SCREEN = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))


class Download(threading.Thread):
    def __init__(self, code: str, image_name: str):
        threading.Thread.__init__(self)
        self.code = code
        self.image_name = image_name

    def run(self):
        """
        Overwrite Thread.run()
        :return: None
        """
        self.download_and_save_image(self.code, self.image_name)

    def download_and_save_image(self, code: str, image_name: str) -> None:
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
            request = requests.get(
                f"https://epic.gsfc.nasa.gov/archive/natural/{code[0:4]}/{code[4:6]}/{code[6:8]}/png/{image_name}.png")
            if request.status_code == 200:
                # path to image
                config.image_path = os.path.join(config.image_path, code + ".png")

                # save image
                with open(config.image_path, "wb") as f:
                    f.write(request.content)

                # resize image
                self.change_size(config.image_path, code)
        except requests.exceptions.ConnectionError:
            pass

    @staticmethod
    def change_size(image_path: str, code: str) -> None:
        """
        Creates a new image from an existing one based on the monitor dimensions and includes
        information about the image's origin
        :param image_path: Path to file
        :param code: Coded date and time
        :return: None
        """
        # images
        image = Image.new("RGB", SCREEN, "black")
        text_image = Image.new("L", (600, 50), 0)
        original_image = Image.open(image_path)

        # scale original image
        original_image = original_image.resize((SCREEN[1], SCREEN[1]))

        # font
        font_size = 15
        font = ImageFont.truetype("arial.ttf", font_size)

        # text to set up
        t = f"This image was taken by NASA's EPIC camera onboard the NOAA DSCOVR spacecraft \n" + \
            f"Date: {code[:4]}-{code[4:6]}-{code[6:8]}    Time: {code[8:10]}:{code[10:12]}"
        txt = ImageDraw.Draw(text_image)
        txt.multiline_text((10, 5), t, fill=255, font=font)
        rotated = text_image.rotate(90, expand=True, fillcolor="white")

        # paste image with text
        image.paste(rotated, (SCREEN[0] - 50, (SCREEN[1] - 600) // 2))

        # paste earth_image
        image.paste(original_image, ((SCREEN[0] - SCREEN[1]) // 2, 0))

        # save image
        image.save(config.image_path)


def main():
    while True:  # Checks for new data every half hour
        check_or_create_image_path()

        check_new_data()
        for thread in threading.enumerate()[2:]:
            thread.join()

        no = len(os.listdir(config.image_path))

        for file in os.listdir(config.image_path):
            ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.join(config.image_path, file), 1 | 2)
            time.sleep(1800 // no)


if __name__ == '__main__':
    main()
