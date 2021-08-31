import os
import junctionart.extensions as extensions
import unittest
import pyodrx
from library.Configuration import Configuration
from junctions.JunctionBuilderFromRoadDefinition import JunctionBuilderFromRoadDefinition


class test_JunctionBuilderFromRoadDefinition(unittest.TestCase):
    def setUp(self):
        self.configuration = Configuration()
        self.builder = JunctionBuilderFromRoadDefinition()
        self.esminiPath = self.configuration.get("esminipath")
        pass


    def test_createIntersectionFromPointsWithRoadDefinition(self):

        roadDefinition = [
            {'x': -30, 'y': 30, 'heading': 3, 'leftLane': 3, 'rightLane': 2, 'medianType': None, 'skipEndpoint': None},
            {'x':   0, 'y': 30, 'heading': 1,  'leftLane': 3, 'rightLane': 3, 'medianType': None, 'skipEndpoint': None},
            {'x':   0, 'y':  0, 'heading': -1.5, 'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            {'x':   -40, 'y': -30, 'heading': -2,  'leftLane': 2, 'rightLane': 2, 'medianType': None, 'skipEndpoint': None},
        ]

        intersection = self.builder.createIntersectionFromPointsWithRoadDefinition(odrID=1,
                                                                          roadDefinition=roadDefinition,
                                                                          firstRoadID=100,
                                                                          straightRoadLength=20,
                                                                          getAsOdr=False)

        print(len(intersection.odr.roads))
        extensions.printRoadPositions(intersection.odr)
        extensions.view_road(intersection.odr, os.path.join('..',self.esminiPath)) 
        pass
        