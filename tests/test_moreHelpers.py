import unittest
import extensions
import os

class test_moreHelper(unittest.TestCase):

    def test_saveRoadImageFromFile(self):

        xodrPath = ""
        outputFile = extensions.saveRoadImageFromFile(xodrPath);

        assert os.path.isfile(outputFile)

