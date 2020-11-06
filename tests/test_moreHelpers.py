import unittest
import extensions
import os

class test_moreHelper(unittest.TestCase):

    def test_saveRoadImageFromFile(self):

        xodrPath = "F:\\myProjects\\av\\esmini\\resources\\xodr\\pythonroad.xodr"
        outputFile = extensions.saveRoadImageFromFile(xodrPath, "F:\\myProjects\\av\\esmini");

        assert os.path.isfile(outputFile)

