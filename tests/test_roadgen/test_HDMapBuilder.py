import unittest

from matplotlib.pyplot import plot
from roadgen.HDMapBuilder import HDMapBuilder
from library.Configuration import Configuration
import extensions, os
import logging
logfile = 'HDMapBuilder.log'
logging.basicConfig(level=logging.INFO, filename=logfile)

class test_HDMapBuilder(unittest.TestCase):

    def setUp(self) -> None:
        self.configuration = Configuration()
        self.hdMapBuilder = HDMapBuilder(50, mapSize=(1000, 1000), cellSize=(100, 100))
        with open(logfile, 'w') as f:
            f.truncate()
        pass

    
    def test_buildMap(self):
        name='first_hd_map'
        odr = self.hdMapBuilder.buildMap(name, plot=False)
        xmlPath = f"output/test_HDMapBuilder-{name}.xodr"
        odr.write_xml(xmlPath)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        pass