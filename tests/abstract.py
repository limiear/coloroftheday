import unittest
import os
import glob


class TestCase(unittest.TestCase):

    def remove(self, filename):
        files = glob.glob(filename)
        map(os.remove, files)
