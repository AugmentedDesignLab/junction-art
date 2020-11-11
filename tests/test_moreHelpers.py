import unittest
import extensions
import os
from library.Configuration import Configuration

class test_moreHelper(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()


    def test_saveRoadImageFromFile(self):

        xodrPath = "F:\\myProjects\\av\\esmini\\resources\\xodr\\pythonroad.xodr"
        outputFile = extensions.saveRoadImageFromFile(xodrPath, self.configuration.get("esminipath"))

        assert os.path.isfile(outputFile)

