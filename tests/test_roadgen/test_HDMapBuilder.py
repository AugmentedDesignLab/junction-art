import unittest

from matplotlib.pyplot import plot
from junctionart.roadgen.HDMapBuilder import HDMapBuilder
from junctionart.library.Configuration import Configuration
import junctionart.extensions as extensions, os
import logging
logfile = 'HDMapBuilder.log'
logging.basicConfig(level=logging.INFO, filename=logfile)

class test_HDMapBuilder(unittest.TestCase):

    def setUp(self) -> None:
        self.configuration = Configuration()
        with open(logfile, 'w') as f:
            f.truncate()
        pass

    
    def test_buildMap(self):
        self.hdMapBuilder = HDMapBuilder(10, mapSize=(120, 120), cellSize=(60, 60))
        name='first_hd_map'
        odr = self.hdMapBuilder.buildMap(name, plot=False)
        xmlPath = f"output/test_HDMapBuilder-{name}.xodr"
        odr.write_xml(xmlPath)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
        pass