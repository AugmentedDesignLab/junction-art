import pyodrx as pyodrx
from junctionart.extensions.CountryCodes import CountryCodes
import unittest
from junctionart.library.Configuration import Configuration
# )
import junctionart.extensions as extensions, os
import math
from junctionart.roundabout.ClassicGenerator import ClassicGenerator
# test
from junctionart.junctions.JunctionBuilder import JunctionBuilder
from junctionart.junctions.LaneBuilder import LaneBuilder
from junctionart.junctions.CurveRoadBuilder import CurveRoadBuilder
from junctionart.junctions.StandardCurvatures import StandardCurvature
from junctionart.junctions.RoadBuilder import RoadBuilder
from junctionart.junctions.StraightRoadBuilder import StraightRoadBuilder
from junctionart.junctions.RoadLinker import RoadLinker
from junctionart.junctions.ODRHelper import ODRHelper
import numpy as np
import random


class test_ClassicGenerator(unittest.TestCase):
    def setUp(self):
        self.configuration = Configuration()

        self.builder = ClassicGenerator(country=CountryCodes.US, laneWidth=3)

        # test
        self.straightbuilder = StraightRoadBuilder()
        self.junctionBuilder = JunctionBuilder()
        self.laneBuilder = LaneBuilder()
        self.curveBuilder = CurveRoadBuilder()
        self.roadBuilder = RoadBuilder()
        pass

    def test_createRoundAboutFromIncidentPoints1(self):

        threePoints = [
            {"x": 80, "y": 20, "heading": math.radians(45),'leftLane': 2, 'rightLane': 2, 'medianType': None, 'skipEndpoint': None},
            {"x": 210, "y": 20, "heading": math.radians(115),'leftLane': 3, 'rightLane': 3, 'medianType': None, 'skipEndpoint': None},
            {"x": 100, "y": 100, "heading": math.radians(300),'leftLane': 4, 'rightLane': 4, 'medianType': None, 'skipEndpoint': None},
            # {"x": 160, "y": 49, "heading": math.radians(300),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            # {"x": 160, "y": 100, "heading": math.radians(220),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
        ]
        odr = self.builder.generateWithRoadDefinition(
            threePoints,
            outgoingLanesMerge=False
        )
        extensions.printRoadPositions(odr)
        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )

    def test_createRoundAboutFromIncidentPoints3(self):

        threePoints = [
            {"x": 440, "y": 500, "heading": math.radians(270),'leftLane': 2, 'rightLane': 2, 'medianType': None, 'skipEndpoint': None},
            # {"x": 600, "y": 200, "heading": math.radians(15),'leftLane': 2, 'rightLane': 3, 'medianType': None, 'skipEndpoint': None},
            {"x": 100, "y": 500, "heading": math.radians(340),'leftLane': 2, 'rightLane': 4, 'medianType': None, 'skipEndpoint': None},
            {"x": 460, "y": 50, "heading": math.radians(90),'leftLane': 2, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            {"x": 160, "y": 100, "heading": math.radians(20),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
        ]
        odr = self.builder.generateWithRoadDefinition(
            threePoints,
            outgoingLanesMerge=False
        )
        extensions.printRoadPositions(odr)
        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )


    def test_createRoundAboutFromIncidentPoints2(self):

        threePoints = [
            {"x": 1, "y": 1, "heading": math.radians(90)},
            {"x": 1, "y": 101, "heading": math.radians(270)},
            # {"x": -90, "y": 11, "heading": math.radians(30)},
        ]
        odr = self.builder.generateWithIncidentPointConfiguration(
            ipConfig=threePoints
        )
        extensions.printRoadPositions(odr)
        extensions.view_road(
            odr, os.path.join("..", self.configuration.get("esminipath"))
        )
    
    