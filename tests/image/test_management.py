"""
Test for image management
"""

from collections import Counter
from unittest import TestCase
from unittest.mock import MagicMock, patch

import parameterized

from image.management import (
    check_or_create_image_path,
    check_wallpapers,
    delete_files,
    generate_code,
)


class TestImageManagement(TestCase):
    """
    Test for image management functions
    """

    @parameterized.parameterized.expand([True, False])  # type: ignore
    @patch("image.management.os")
    def test_path_creation(self, path_exists: bool, os_mock: MagicMock) -> None:
        """
        Tests for function check_or_create_image_path
        :param path_exists: return value from mock
        :param os_mock: patch for mock
        :return:
        """
        os_mock.path.exists.return_value = path_exists
        os_mock.makedirs.return_value = None
        check_or_create_image_path()
        self.assertEqual(os_mock.makedirs.called, not path_exists)

    @parameterized.parameterized.expand(
        [[["file", "file", "file"]], [["file", "dir", "dir"]], [["dir", "file", "file"]]]
    )  # type: ignore
    @patch("image.management.os")
    @patch("image.management.shutil")
    def test_delete_files(self, files: list[str], shutil_mock: MagicMock, os_mock: MagicMock) -> None:
        """
        Check if delete_files function can delete file or directory
        :param files: list of name to be concatenated with image_dir and deleted
        :param shutil_mock: mock for shutil module
        :param os_mock: mock for os module
        :return:
        """
        os_mock.remove.return_value = None
        shutil_mock.rmtree.return_value = None
        os_mock.path.join.side_effect = lambda _, value: value
        os_mock.path.isfile.side_effect = lambda value: value.endswith("file")
        delete_files(files)
        counter = Counter(files)
        self.assertEqual(os_mock.remove.call_count, counter["file"])
        self.assertEqual(shutil_mock.rmtree.call_count, counter["dir"])

    def test_generate_code(self) -> None:
        """
        Generate code should parse str from API to str
        :return:
        """
        code = generate_code(date="2024-12-12 00:00:00")
        self.assertEqual("20241212000000", code)

    @parameterized.parameterized.expand(["", "00:00:00", "2024-12-12", "this is not date"])  # type: ignore
    def test_generate_code_wrong_date(self, date: str) -> None:
        """
        Check if generate code not works for wrong date format
        :param date: date to be parsed
        :return:
        """
        with self.assertRaises(ValueError):
            generate_code(date=date)

    @parameterized.parameterized.expand(
        [
            [["1_invalid", "2_invalid", "3_invalid"], None, [], ["1_invalid", "2_invalid", "3_invalid"]],
            [
                ["20241212000000", "2_invalid", "3_invalid"],
                "20241212000000",
                ["20241212000000"],
                ["2_invalid", "3_invalid"],
            ],
            [
                ["20241212000000", "20241212000001", "3_invalid"],
                "20241212000001",
                ["20241212000000", "20241212000001"],
                ["3_invalid"],
            ],
        ]
    )  # type: ignore
    @patch("image.management.validate_file")
    def test_check_wallpapers(
        self,
        files: list[str],
        oldest_file: str | None,
        valid: list[str],
        invalid: list[str],
        validator_mock: MagicMock,
        os_mock: MagicMock,
    ) -> None:
        """
        Test if check_wallpapers run validate_file function and report status in correct way
        :param files: filenames to validate
        :param oldest_file: the oldest file
        :param valid: list of valid files
        :param invalid: list of invalid files
        :param validator_mock: mock for validator
        :param os_mock: unused mock for os
        :return:
        """
        os_mock.listdir.return_value = files
        validator_mock.side_effect = lambda filename: not filename.endswith("invalid")
        result = check_wallpapers()
        self.assertEqual(oldest_file, result[0])
        self.assertListEqual(valid, result[1])
        self.assertListEqual(invalid, result[2])
