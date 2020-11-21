import unittest
from junctions.JunctionHarvester import JunctionHarvester
import extensions, os
import numpy as np
from library.Configuration import Configuration

class test_JunctionHarvester(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        outputDir= os.path.join(os.getcwd(), 'output')
        lastId = 0
        self.harvester = JunctionHarvester(outputDir=outputDir, 
                                        outputPrefix='test_', 
                                        lastId=lastId,
                                        minAngle = np.pi / 30, 
                                        maxAngle = np.pi)
        pass


    def test_drawLikeAPainter2L(self):
        odr = self.harvester.drawLikeAPainter2L(4)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))


    def test_drawLikeAPainter2LWihtoutInternalConnections(self):
        odr = self.harvester.drawLikeAPainter2L(5, internalConnections=False)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr,os.path.join('..',self.configuration.get("esminipath")))
