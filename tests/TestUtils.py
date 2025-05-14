
import os
import pathlib
import unittest

import io_scene_ogex

__author__ = 'Jonathan Hale'


class OgexExporterTest(unittest.TestCase):

    no_delete = False

    @classmethod
    def setUpClass(self):
        io_scene_ogex.register()

    @classmethod
    def tearDownClass(cls):
        io_scene_ogex.unregister()

    def tearDown(self):
        if os.path.isfile(self.filename) and not self.no_delete:
            os.remove(self.filename)

    def readContents(self, filename):
        """
        Open, read the contents and then close a file.
        :param filename: name of the file to read the contents of
        :return: Contents of the file with given filename
        """
        with open(filename) as f:
            contents = f.readlines()
        return contents

    def assertFilesEqual(self, test_filename, expected_filename):
        """
        Check whether the contents of two files are equal
        :param test_filename: name of the file to test
        :param expected_filename: name of the file containing expected content
        """
        test_file_contents = self.readContents(test_filename)
        expected_file_contents = self.readContents(expected_filename)
        self.assertEqual(len(test_file_contents), len(expected_file_contents))
        # NOTE(rosado): assertEquals hang forever here, possibly because unitttest
        # attempts to make a diff? Haven't debugged it - will replace line by line
        # comparisons anyway...
        self.fail('Failing on purpose, tests need updating')

    def file_path(self, file_name) -> pathlib.Path:
        return pathlib.Path(self.base_dir) / file_name
        

