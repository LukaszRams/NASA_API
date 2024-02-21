"""
Image operations
"""

import datetime

from PIL import Image, ImageDraw, ImageFont

from config import config
from logger import app_logger


def resize_image(image_path: str) -> Image.Image:
    """
    Open image and resize to the screen size (image is square)
    :param image_path: path to image
    :return: resized image
    """
    app_logger.debug("Resizing original image")
    image = Image.open(image_path)
    return image.resize((config.resolution[1], config.resolution[1]))


def get_description_image(code: str) -> Image.Image:
    """
    Creates image with description
    :param code: code to be parsed (date and time of image)
    :return: created image
    """
    app_logger.debug("Creating description image")
    date_and_time = datetime.datetime.strptime(code, "%Y%m%d%H%M%S")
    # font
    font_size = 15
    font = ImageFont.truetype("arial.ttf", font_size)

    # text to set up
    text_image = Image.new("L", (600, 50), 0)
    t = (
        "This image was taken by NASA's EPIC camera onboard the NOAA DSCOVR spacecraft \n"
        + f"Date: {date_and_time.date()}    Time: {date_and_time.time()}"
    )
    txt = ImageDraw.Draw(text_image)
    txt.multiline_text((10, 5), t, fill=255, font=font)
    return text_image.rotate(90, expand=True, fillcolor="white")


def connect_images(earth_image: Image.Image, description_image: Image.Image) -> Image.Image:
    """
    Create background image and paste photo and description on it
    :param earth_image: image of the earth
    :param description_image: image with description
    :return: connected images
    """
    app_logger.debug("Connecting images")
    # paste image with text
    image = Image.new("RGB", config.resolution, "black")
    image.paste(
        description_image,
        (config.resolution[0] - 50, (config.resolution[1] - 600) // 2),
    )

    # paste earth_image
    image.paste(earth_image, ((config.resolution[0] - config.resolution[1]) // 2, 0))
    return image


def process_image(image_path: str, code: str) -> None:
    """
    Creates a new image from an existing one based on the monitor dimensions and includes
    information about the image's origin
    :param image_path: Path to file
    :param code: Coded date and time
    :return: None
    """
    # images
    original_image = resize_image(image_path=image_path)
    text_image = get_description_image(code=code)
    image = connect_images(earth_image=original_image, description_image=text_image)

    # save image
    image.save(image_path)
    app_logger.debug("Connected images saved")
