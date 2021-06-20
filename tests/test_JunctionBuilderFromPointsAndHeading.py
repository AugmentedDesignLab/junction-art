
from extensions.CountryCodes import CountryCodes
import unittest
from library.Configuration import Configuration
from junctions.JunctionBuilderFromPointsAndHeading import JunctionBuilderFromPointsAndHeading
import extensions, os
import math

class test_JunctionBuilderFromPointsAndHeading(unittest.TestCase):
    def setUp(self):
        self.configuration = Configuration()
        self.builder = JunctionBuilderFromPointsAndHeading(country=CountryCodes.US,
                                                            laneWidth=3)
        pass

    def test_createJunctionFromPoints(self):

        threePoints = [
            [-30,  30, math.radians(135)],
            [ 30,  40, math.radians(45)],
            [  0,  -40,  math.radians(270)]
        ]
        odr = self.builder.createIntersectionFromPoints(odrID=0,
                                                        points=threePoints,
                                                        straightRoadLen=30,
                                                        firstRoadID=0,
                                                        maxLanePerSide=1,
                                                        minLanePerSide=0,
                                                        skipEndpoint=None)
        extensions.printRoadPositions(odr)
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))


        points1 = [
            [-30,  30, math.radians(135)],
            [-20,  40, math.radians(120)],
            [  0,  45,  math.radians(90)],
            [ 30,  30,  math.radians(45)],
            [  0, -30, math.radians(225)]
        ]


        odr = self.builder.createIntersectionFromPoints(odrID=0,
                                                        points=points1,
                                                        straightRoadLen=30,
                                                        firstRoadID=0,
                                                        maxLanePerSide=1,
                                                        minLanePerSide=0,
                                                        skipEndpoint=None)
        # extensions.printRoadPositions(odr)
        # extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath"))) 




        points2 = [
            [-10,   0, math.radians(180)],
            [-5.25322,  5.25322, math.radians(135)],
            [  0,  10,  math.radians(90)],
            [ 5.25322,  5.25322,  math.radians(45)],
            [  10, 0, math.radians(0)],
            [  5.25322, -5.25322, math.radians(315)],
            [  0, -10, math.radians(270)],
            [  -5.25322, -5.25322, math.radians(225)],
        ]

        
        pass