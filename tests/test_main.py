"""
Test main.py
"""

import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

import parameterized

from config import config
from main import display_wallpapers


class TestDisplayWallpapers(TestCase):
    """
    Test function display_wallpapers from main.py
    """

    @parameterized.parameterized.expand(
        [
            (1, 1800),
            (2, 900),
            (3, 600),
            (10, 180),
            (11, 163),
            (12, 150),
            (13, 138),
            (14, 128),
            (15, 120),
        ]
    )  # type: ignore
    def test_for_happy_path(
        self,
        number_of_files: int,
        delay_time: int,
    ) -> None:
        """
        Test if sleep time is calculated properly and called correct number of times. Check parameter of
        mock.

        Happy path - we have images in folder

        :param number_of_files: number of files to be detected in image directory
        :param delay_time: expected arg for time.sleep()
        :return:
        """

        with (
            patch("main.ctypes.windll.user32.SystemParametersInfoW") as system_parameters_mock,
            patch("main.time.sleep") as sleep_mock,
            patch("main.os.listdir") as listdir_mock,
        ):
            filenames = [f"{i}.jpg" for i in range(number_of_files)]
            listdir_mock.return_value = filenames
            sleep_mock.return_value = None
            system_parameters_mock.return_value = None
            display_wallpapers()
            base_path = config.image_path
            for counter, file in enumerate(filenames):
                set_wallpaper = system_parameters_mock.call_args_list[counter].args[2]
                self.assertEqual(delay_time, sleep_mock.call_args_list[counter].args[0])
                self.assertEqual(os.path.join(base_path, file), set_wallpaper)
            self.assertEqual(number_of_files, system_parameters_mock.call_count)

    def test_no_file_in_image_directory(self) -> None:
        """
        Check if function no throw error when no file in directory and no call set wallpaper
        In this case function should return None and app should download files from API
        :return:
        """
        with (
            patch("main.ctypes.windll.user32.SystemParametersInfoW") as system_parameters_mock,
            patch("main.time.sleep") as sleep_mock,
            patch("main.os.listdir") as listdir_mock,
        ):
            listdir_mock.return_value = []
            display_wallpapers()
            self.assertEqual(sleep_mock.call_count, 0)
            self.assertEqual(system_parameters_mock.call_count, 0)

    @patch("main.delete_files")
    def test_system_parameters_side_effect(self, delete_files_mock: MagicMock) -> None:
        """
        Check if function properly remove file when error while set wallpaper.
        :param delete_files_mock: mock delete function
        :return:
        """
        with (
            patch("main.ctypes.windll.user32.SystemParametersInfoW") as system_parameters_mock,
            patch("main.time.sleep") as sleep_mock,
            patch("main.os.listdir") as listdir_mock,
        ):
            listdir_mock.return_value = ["not_existing_file_1.png", "not_existing_file_2.png"]
            sleep_mock.return_value = None
            delete_files_mock.return_value = None
            system_parameters_mock.return_value = None
            system_parameters_mock.side_effect = OSError()
            display_wallpapers()
            self.assertEqual(sleep_mock.call_count, 0)
            self.assertEqual(system_parameters_mock.call_count, 2)
            self.assertEqual(delete_files_mock.call_count, 2)
