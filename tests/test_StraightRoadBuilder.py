import unittest, os
from junctions.StraightRoadBuilder import StraightRoadBuilder
from scipy.interpolate import CubicHermiteSpline
from junctions.JunctionHarvester import JunctionHarvester
import numpy as np
import pyodrx, extensions
from junctions.JunctionBuilder import JunctionBuilder
from library.Configuration import Configuration
import junctions

from junctions.Direction import CircularDirection


class test_StraightRoadBuilder(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()

        self.straightRoadBuilder = StraightRoadBuilder()

    

    def test_LeftTurnLanes(self):
        
        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, leftTurnLane=True))

        odrName = "test_LeftTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-LeftTurnLane.xodr"
        odr.write_xml(xmlPath)

    def test_RightTurnLanes(self):
        
        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, rightTurnLane=True))

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-RightTurnLane.xodr"
        odr.write_xml(xmlPath)