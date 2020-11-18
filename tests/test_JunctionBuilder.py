import unittest

import numpy as np
import os, dill
import pyodrx 
from junctions.JunctionMerger import JunctionMerger
import extensions
from library.Configuration import Configuration
from junctions.JunctionBuilder import JunctionBuilder

class test_JunctionMerger(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        self.junctionBuilder = JunctionBuilder()

    
    def test_buildSimpleRoundAbout(self):

        numRoads = 7
        odr = self.junctionBuilder.buildSimpleRoundAbout(odrId=0, numRoads=numRoads, radius=10)
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        
        odr.write_xml(f"output/test_buildSimpleRoundAbout-{numRoads}.xodr")
