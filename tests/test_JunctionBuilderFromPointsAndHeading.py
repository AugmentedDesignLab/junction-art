import pyodrx as pyodrx
from junctionart.extensions.CountryCodes import CountryCodes
import unittest
from junctionart.library.Configuration import Configuration
from junctionart.junctions.JunctionBuilderFromPointsAndHeading import JunctionBuilderFromPointsAndHeading
# )
import junctionart.extensions as extensions, os
import math
# import junctionart.roundabout as roundabout
from junctionart.roundabout.ClassicGenerator import ClassicGenerator
# from junctionart.roundabout import ClassicGenerator


class test_JunctionBuilderFromPointsAndHeading(unittest.TestCase):
    def setUp(self):
        self.configuration = Configuration()
        self.builder = JunctionBuilderFromPointsAndHeading(
            country=CountryCodes.US, laneWidth=3
        )

        pass


    def test_createJunctionFromPoints(self):

        threePoints = [
            [-30, 30, math.radians(135)],
            [30, 40, math.radians(45)],
            [0, -40, math.radians(270)],
        ]
        odr = self.builder.createIntersectionFromPoints(
            odrID=0,
            points=threePoints,
            straightRoadLen=30,
            firstRoadID=0,
            maxLanePerSide=1,
            minLanePerSide=0,
            skipEndpoint=None,
        )
        extensions.printRoadPositions(odr)
        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )

        points1 = [
            [-30, 30, math.radians(135)],
            [-20, 40, math.radians(120)],
            [0, 45, math.radians(90)],
            [30, 30, math.radians(45)],
            [0, -30, math.radians(225)],
        ]

        odr = self.builder.createIntersectionFromPoints(
            odrID=0,
            points=points1,
            straightRoadLen=30,
            firstRoadID=0,
            maxLanePerSide=1,
            minLanePerSide=0,
            skipEndpoint=None,
        )
        # extensions.printRoadPositions(odr)
        # extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))

        points2 = [
            [-10, 0, math.radians(180)],
            [-5.25322, 5.25322, math.radians(135)],
            [0, 10, math.radians(90)],
            [5.25322, 5.25322, math.radians(45)],
            [10, 0, math.radians(0)],
            [5.25322, -5.25322, math.radians(315)],
            [0, -10, math.radians(270)],
            [-5.25322, -5.25322, math.radians(225)],
        ]

        pass

    def test_createIntersectionFromPointsWithRoadDefinition(self):

        roadDefinition = [
            {
                "x": -30,
                "y": 30,
                "heading": 2,
                "leftLane": 2,
                "rightLane": 2,
                "medianType": "partial",
                "skipEndpoint": pyodrx.ContactPoint.start,
            },
            {
                "x": 0,
                "y": 30,
                "heading": 1,
                "leftLane": 2,
                "rightLane": 3,
                "medianType": None,
                "skipEndpoint": None,
            },
            {
                "x": 0,
                "y": 0,
                "heading": -1.5,
                "leftLane": 1,
                "rightLane": 1,
                "medianType": "partial",
                "skipEndpoint": pyodrx.ContactPoint.end,
            },
            # {'x':   -40, 'y': -30, 'heading': -2,  'leftLane': 2, 'rightLane': 2, 'medianType': None, 'skipEndpoint': None},
        ]

        odr = self.builder.createIntersectionFromPointsWithRoadDefinition(
            odrID=0,
            firstRoadId=100,
            roadDefinition=roadDefinition,
            straightRoadLen=40,
            getAsOdr=True,
        )
        extensions.printRoadPositions(odr)
        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )
        pass

    def test_another(self):

        # roadDefs = [{'x': 14.993254552835499, 'y': 100.44979763658513, 'heading': 0.029991004856882365, 'leftLane': 1, 'rightLane': 1, 'medianType': 'partial', 'skipEndpoint': pyodrx.ContactPoint.end},
        #     {'x': 9.18485099360515e-16, 'y': 115.0, 'heading': 1.5707963267948966, 'leftLane': 1, 'rightLane': 1, 'medianType': 'partial', 'skipEndpoint': pyodrx.ContactPoint.end},
        #     {'x': 9.18485099360515e-16, 'y': 85, 'heading': 4.71238898038469, 'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None}
        # ]
        # roadDefs = [
        #     {'x': 246.68903179808726, 'y': 132.06133739837088, 'heading': 1.6453885407740492, 'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
        #     {'x': 232.19888458406353, 'y': 121.39515908838844, 'heading': 3.0945804556103114, 'leftLane': 2, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
        #     {'x': 246.87298086638685, 'y': 106.49432991649509, 'heading': 4.665376782405206, 'leftLane': 0, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
        #     {'x': 257.9417055131878, 'y': 120.18404011259686, 'heading': 6.236173109200104, 'leftLane': 1, 'rightLane': 0, 'medianType': None, 'skipEndpoint': None}
        # ]

        roadDefs = [
            {
                "x": 246.68903179808726,
                "y": 132.06133739837088,
                "heading": 0,
                "leftLane": 1,
                "rightLane": 1,
                "medianType": None,
                "skipEndpoint": None,
            },
            {
                "x": 257.9417055131878,
                "y": 120.18404011259686,
                "heading": -1,
                "leftLane": 1,
                "rightLane": 0,
                "medianType": None,
                "skipEndpoint": None,
            },
            {
                "x": 246.87298086638685,
                "y": 106.49432991649509,
                "heading": -1.5,
                "leftLane": 0,
                "rightLane": 1,
                "medianType": None,
                "skipEndpoint": None,
            },
            {
                "x": 232.19888458406353,
                "y": 121.39515908838844,
                "heading": -2,
                "leftLane": 2,
                "rightLane": 1,
                "medianType": None,
                "skipEndpoint": None,
            },
        ]

        intersection = self.builder.createIntersectionFromPointsWithRoadDefinition(
            odrID=0,
            roadDefinition=roadDefs,
            firstRoadId=100,
            straightRoadLen=10,
            getAsOdr=False,
        )
        odr = intersection.odr
        xmlPath = f"output/test_another.xodr"
        odr.write_xml(xmlPath)
        extensions.printRoadPositions(odr)
        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )

    def test_validateRoadDefinition(self):

        # A good one
        # roadDefs = [
        #     {'x': 246.68903179808726, 'y': 132.06133739837088, 'heading': 1.6453885407740492, 'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
        #     {'x': 257.9417055131878, 'y': 120.18404011259686, 'heading': 6.236173109200104, 'leftLane': 1, 'rightLane': 0, 'medianType': None, 'skipEndpoint': None},
        #     {'x': 246.87298086638685, 'y': 106.49432991649509, 'heading': 4.665376782405206, 'leftLane': 0, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
        #     {'x': 232.19888458406353, 'y': 121.39515908838844, 'heading': 3.0945804556103114, 'leftLane': 2, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None}
        # ]
        roadDefs = [
            {
                "x": 246.68903179808726,
                "y": 132.06133739837088,
                "heading": 0,
                "leftLane": 1,
                "rightLane": 1,
                "medianType": None,
                "skipEndpoint": None,
            },
            {
                "x": 257.9417055131878,
                "y": 120.18404011259686,
                "heading": -1,
                "leftLane": 1,
                "rightLane": 0,
                "medianType": None,
                "skipEndpoint": None,
            },
            {
                "x": 246.87298086638685,
                "y": 106.49432991649509,
                "heading": -1.5,
                "leftLane": 0,
                "rightLane": 1,
                "medianType": None,
                "skipEndpoint": None,
            },
            {
                "x": 232.19888458406353,
                "y": 121.39515908838844,
                "heading": -2,
                "leftLane": 2,
                "rightLane": 1,
                "medianType": None,
                "skipEndpoint": None,
            },
        ]

        self.builder.validateRoadDefinition(roadDefs)

    
