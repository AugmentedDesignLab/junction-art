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

        numRoads = 3
        odr = self.junctionBuilder.buildSimpleRoundAbout(odrId=0, numRoads=numRoads, radius=10)
        xmlPath = f"output/test_buildSimpleRoundAbout-{numRoads}.xodr"
        odr.write_xml(xmlPath)
        
        extensions.saveRoadImageFromFile(xmlPath, self.esminiPath)
        extensions.view_road(odr, os.path.join('..', self.esminiPath))

        
