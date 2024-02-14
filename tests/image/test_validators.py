"""
Test for image validators
"""

import os
from datetime import timedelta
from unittest import TestCase
from unittest.mock import patch

import PIL.Image
from parameterized import parameterized

from image.validators import *


class TestValidators(TestCase):
    """
    Test if validators works as expected
    """

    def setUp(self) -> None:
        """
        Create some broken files for further tests
        """
        self.not_existing_file = "this_file_not_exist"
        self.empty_file = os.path.join(config.image_path, "empty_file.png")

        with open(self.empty_file, "w") as fp:
            pass

        self.broken_file = os.path.join(config.image_path, "broken_file.png")
        with open(self.broken_file, "w") as fp:
            fp.write("some text")

        # for correct file name we need date in future
        time = datetime.now() + timedelta(days=3)
        filename_from_time = time.strftime("%Y%m%d%H%M%S") + ".png"
        self.correct_file = os.path.join(config.image_path, filename_from_time)
        image = PIL.Image.new("RGB", config.resolution, (0, 0, 0))
        image.save(self.correct_file)

    def tearDown(self) -> None:
        """
        Delete broken files
        :return:
        """
        os.remove(self.broken_file)
        os.remove(self.empty_file)
        os.remove(self.correct_file)

    @parameterized.expand(
        [
            ("file_without_extension", False),
            ("", False),  # blank filename
            ("file_with_extension.jpg", False),
            ("file_with_extension.jpeg", False),
            ("file_with_extension.mp4", False),
            ("file_with_extension.gif", False),
            ("file_with_extension.svg", False),
            ("file_with.png_in_the_middle", False),
            ("file.png", True),
        ]
    )
    def test_file_extension_validator(self, filename: str, is_valid: bool) -> None:
        """
        Function check_file_extension should return True if filename ends with .png
        :param filename: filename to valid
        :param is_valid: result of the test
        :return:
        """
        status = check_file_extension(filename)
        self.assertEqual(is_valid, status)

    @parameterized.expand(
        [
            ("", False),  # blank filename
            ("17_characters.png", False),
            ("19_characters__.png", False),
            ("YYYYmmddHHMMSS.mp4", True),
        ]
    )
    def test_length_of_filename_validator(self, filename: str, is_valid: bool) -> None:
        """
        Filenames has format YYYmmddHHMMSS.png so its length should be 18 characters
        :param filename: filename to valid
        :param is_valid: correct result of validation
        :return:
        """
        status = check_length_of_file(filename)
        self.assertEqual(is_valid, status)

    @parameterized.expand(
        [
            ("", False),  # blank filename
            ("123456789abcde.png", False),
            ("123456789abcd.png", False),
            ("1234567891234.png", False),
            ("abcdefghijklmn.png", False),
            ("01234567891234.mp4", True),
            ("12345678912345.mp4", True),
        ]
    )
    def test_filename_without_extension_validator(self, filename: str, is_valid: bool) -> None:
        """
        Filenames without extension might be mapped to int
        :param filename: filename to valid
        :param is_valid: correct result of validation
        :return:
        """
        status = check_filename_without_extension(filename)
        self.assertEqual(is_valid, status)

    @parameterized.expand(
        [
            ("20231212121222.png", datetime(2024, 10, 10, 12, 12, 12), False),  # blank filename
            ("20241212121222.png", datetime(2022, 10, 10, 12, 12, 12), True),
        ]
    )
    @patch("image.validators.datetime")
    def test_check_date_of_image(
        self, filename: str, datetime_now: datetime, is_valid: bool, datetime_now_mock: patch
    ) -> None:
        """
        Test if validator make comparison between datetime and file
        :param filename: filename to valid
        :param datetime_now: datetime mock result
        :param is_valid: correct status of validation
        :param datetime_now_mock: mock patch
        :return:
        """
        datetime_now_mock.now.return_value = datetime_now
        status = check_date_of_image(filename)
        self.assertEqual(is_valid, status)

    def test_check_if_image_is_not_broken(self) -> None:
        """
        Test if validator detect broken files
        :return:
        """
        self.assertEqual(False, check_if_file_is_not_broken(self.not_existing_file))
        self.assertEqual(False, check_if_file_is_not_broken(self.broken_file))
        self.assertEqual(False, check_if_file_is_not_broken(self.empty_file))

    def test_check_if_image_is_not_broken_correct_image(self) -> None:
        """
        Test if validator detect broken files
        :return:
        """
        self.assertEqual(True, check_if_file_is_not_broken(self.correct_file))

    @parameterized.expand(
        [
            [False, [False, True, True, True, True]],
            [False, [True, False, True, True, True]],
            [False, [True, True, False, True, True]],
            [False, [True, True, True, False, True]],
            [False, [True, True, True, True, False]],
            [False, [True, False, True, False, True]],
            [False, [False, True, True, True, False]],
            # only one correct
            [True, [True, True, True, True, True]],
        ]
    )
    @patch("image.validators.check_file_extension")  # mock_validator_1
    @patch("image.validators.check_length_of_file")  # mock_validator_2
    @patch("image.validators.check_filename_without_extension")  # mock_validator_3
    @patch("image.validators.check_date_of_image")  # mock_validator_4
    @patch("image.validators.check_if_file_is_not_broken")  # mock_validator_5
    def test_validate_file(
        self,
        is_valid: bool,
        validator_results: list[bool],
        mock_validator_1: patch,
        mock_validator_2: patch,
        mock_validator_3: patch,
        mock_validator_4: patch,
        mock_validator_5: patch,
    ) -> None:
        """
        Test for validate file. All validators are patched, so we set return values and check validation output
        :return:
        """
        mock_config = {"__name__": "", "__doc__": ""}
        mocks = [mock_validator_1, mock_validator_2, mock_validator_3, mock_validator_4, mock_validator_5]
        for mock, return_value in zip(mocks, validator_results):
            mock.return_value = return_value
            mock.configure_mock(**mock_config)

        status = validate_file("")
        self.assertEqual(is_valid, status)
