
import os
import pathlib
import unittest

import io_scene_ogex

import tests.oddl.oddl as oddl

__author__ = 'Jonathan Hale, Roland Sadowski'


class OgexExporterTest(unittest.TestCase):

    no_delete = False
    
    @staticmethod
    def base_dir_for(file):
        """Pass __file__"""
        return os.path.dirname(os.path.realpath(file))

    @classmethod
    def setUpClass(self):
        io_scene_ogex.register()

    @classmethod
    def tearDownClass(cls):
        io_scene_ogex.unregister()

    def tearDown(self):
        files = []
        if hasattr(self, "filename"):
            if os.path.isfile(self.filename) and not self.no_delete:
                files.append(self.filename)
        
        if hasattr(self, "output_file_name"):
            full_path = self.file_path(self.output_file_name)
            if os.path.isfile(full_path) and not self.no_delete:
                files.append(full_path)

        for f in files:
            os.remove(f)

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
        """Returns path to file in directory of currently executing test.
        Expects self.base_dir to be set"""
        return pathlib.Path(self.base_dir) / file_name
    
    
    def parse_ogex_file(self, path: pathlib.Path) -> list[oddl.Structure]:
        with open(path, "r") as f:
            ogex_str = f.read()
        
        ctx = oddl.ParseContext(ogex_str)
        stream = list(oddl.parse_as_stream(ctx))
        return oddl.parse_stream(stream)
        

