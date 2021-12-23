import requests
import ctypes
from PIL import Image, ImageDraw, ImageFont
import shutil
import os
from datetime import datetime
from typing import List, Tuple
import threading
import time
import sys


import socket
import win32serviceutil
import servicemanager
import win32event
import win32service


IMAGE_PATH = os.path.join(os.getenv("LocalAppData"), "NASA_Api")
SCREEN = None


def check_or_create_image_path() -> None:
    """
    Checks if the folder for graphics exists if not creates it
    :return: None
    """
    if not os.path.exists(IMAGE_PATH):
        os.makedirs(IMAGE_PATH)


def check_new_data() -> None:
    """
    Checks whether new data are available and, if available, triggers recording
    :return: None
    """

    # get last image
    request = requests.get("https://epic.gsfc.nasa.gov/api/natural")
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


def check_wallpapers() -> Tuple[str, List[str], List[str]]:
    """
    Retrieves the date of the latest image from the folder, if the date is newer than the current date, forces a new
    image to be downloaded and returns error information about the folder
    :return: latest, valid, invalid
    """
    files = os.listdir(IMAGE_PATH)

    # valdate files
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
        if Image.open(os.path.join(IMAGE_PATH, file)).size != SCREEN:
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
        path = os.path.join(IMAGE_PATH, file)
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

        request = requests.get(
            f"https://epic.gsfc.nasa.gov/archive/natural/{code[0:4]}/{code[4:6]}/{code[6:8]}/png/{image_name}.png")

        # check if get return succes code
        if request.status_code == 200:
            # path to image
            image_path = os.path.join(IMAGE_PATH, code + ".png")

            # save image
            with open(image_path, "wb") as f:
                f.write(request.content)

            # resize image
            self.change_size(image_path, code)


    def change_size(self, image_path: str, code: str) -> None:
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
        image.paste(rotated, (SCREEN[0]-50, (SCREEN[1]-600)//2))

        # paste earth_image
        image.paste(original_image, ((SCREEN[0]-SCREEN[1])//2, 0))

        # save image
        image.save(image_path)



class WinService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'nasaApi'
    _svc_display_name_ = 'NASA Api'
    _svc_description_ = 'Service using EPIC DAILY "BLUE MARBLE" API to download ' \
                        'satellite images of the Earth and set them as wallpaper'

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        set_screen_resolution()

        while True:  # Checks for new data every half hour
            check_or_create_image_path()
            check_new_data()

            for thread in threading.enumerate()[1:]:
                thread.join()

            no = len(os.listdir(IMAGE_PATH))

            for file in os.listdir(IMAGE_PATH):
                ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.join(IMAGE_PATH, file), 0)
                if win32event.WaitForSingleObject(self.hWaitStop, (1800*1000) // no) == win32event.WAIT_OBJECT_0:
                    self.stop = True
                    break
            if self.stop:
                self.stop = False
                break
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


def main():
    if len(sys.argv) > 1:
        win32serviceutil.HandleCommandLine(WinService)
    else:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(WinService)
        servicemanager.StartServiceCtrlDispatcher()
