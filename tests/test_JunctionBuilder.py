import unittest

import numpy as np
import os, dill
import pyodrx 
from junctions.JunctionMerger import JunctionMerger
import extensions
from library.Configuration import Configuration
from junctions.JunctionBuilder import JunctionBuilder

class test_JunctionBuilder(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        self.junctionBuilder = JunctionBuilder()
        self.esminiPath = self.configuration.get("esminipath")

    
    def test_buildSimpleRoundAbout(self):

        numRoads = 10
        odr = self.junctionBuilder.buildSimpleRoundAbout(odrId=0, numRoads=numRoads, radius=10, cp1=pyodrx.ContactPoint.end)
        xmlPath = f"output/test-SimpleRoundAbout-{numRoads}.xodr"
        odr.write_xml(xmlPath)

        extensions.printRoadPositions(odr)
        extensions.saveRoadImageFromFile(xmlPath, self.esminiPath)
        extensions.view_road(odr, os.path.join('..', self.esminiPath))

        
