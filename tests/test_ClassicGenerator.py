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
            {"x": 80, "y": 20, "heading": math.radians(0)},
            {"x": 210, "y": 20, "heading": math.radians(135)},
            {"x": 100, "y": 100, "heading": math.radians(270)},
            {"x": 160, "y": -250, "heading": math.radians(90)},
        ]
        odr = self.builder.generateWithIncidentPointConfiguration(
            ipConfig=threePoints
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
    
    