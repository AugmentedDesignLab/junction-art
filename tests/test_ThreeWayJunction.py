import unittest
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
from junctions.threeWayJunction import threeWayJunction
import extensions, os
import numpy as np
from library.Configuration import Configuration
from junctions.LaneConfiguration import LaneConfigurationStrategies
import pyodrx
import logging
logging.basicConfig(level=logging.INFO)

class test_ThreeWayJunction(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        outputDir= os.path.join(os.getcwd(), 'output')
        lastId = 0
        self.seed = 2
        self.builder = threeWayJunction.ThreeWayJunction(
                                                        minAngle=np.pi/9, 
                                                        maxAngle=np.pi * .25,
                                                        straightRoadLen=10
                                                        )

        self.randomState =self.configuration.get("random_state")

        pass

    def test_ThreeWayJunctionWithAngle(self):
        angleBetweenRoads = np.pi/4

        odr = self.builder.ThreeWayJunctionWithAngle(odrId=1,
                                                    angleBetweenRoads=np.pi/3,
                                                    maxLanePerSide=2,
                                                    minLanePerSide=1,
                                                    cp1=pyodrx.ContactPoint.end)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))
        extensions.view_road_odrviewer(odr, os.path.join('..',self.configuration.get("esminipath")))
        xmlPath = f"output/test_ThreeWayJunctionWithAngle.xodr"
        odr.write_xml(xmlPath)