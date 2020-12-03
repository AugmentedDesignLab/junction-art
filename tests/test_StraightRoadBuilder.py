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
from junctions.RoadLinker import RoadLinker


class test_StraightRoadBuilder(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()

        self.straightRoadBuilder = StraightRoadBuilder()
        self.roadLinker = RoadLinker()

    

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


    def test_TurnLanes(self):
        
        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, rightTurnLane=True, leftTurnLane=True))
        roads.append(self.straightRoadBuilder.createStraightRoad(1, length = 10, n_lanes=2))

        roads[0].updateSuccessor(pyodrx.ElementType.road, roads[1].id, pyodrx.ContactPoint.start)
        roads[1].updatePredecessor(pyodrx.ElementType.road, roads[0].id, pyodrx.ContactPoint.end)

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-TurnLanes.xodr"
        odr.write_xml(xmlPath)


    def test_MergeLanes(self):
        
        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, leftMergeLane=True))

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-LeftMergeLane.xodr"
        odr.write_xml(xmlPath)

        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, rightMergeLane=True))

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-RightMergeLanes.xodr"
        odr.write_xml(xmlPath)

        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, n_lanes=2))
        roads.append(self.straightRoadBuilder.createStraightRoad(1, length = 10, leftMergeLane=True, rightMergeLane=True))

        roads[0].updateSuccessor(pyodrx.ElementType.road, roads[1].id, pyodrx.ContactPoint.start)
        roads[1].updatePredecessor(pyodrx.ElementType.road, roads[0].id, pyodrx.ContactPoint.end)

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-MergeLanes.xodr"
        odr.write_xml(xmlPath)


    def test_mergeAndTurns(self):

        roads = []
        roads.append(self.straightRoadBuilder.createStraightRoad(0, length = 10, n_lanes=2))
        roads.append(self.straightRoadBuilder.createStraightRoad(1, length = 10, leftMergeLane=True, rightMergeLane=True))
        roads.append(self.straightRoadBuilder.createStraightRoad(2, length = 10))
        roads.append(self.straightRoadBuilder.createStraightRoad(3, length = 10, rightTurnLane=True, leftTurnLane=True))
        roads.append(self.straightRoadBuilder.createStraightRoad(4, length = 10, n_lanes=2))

        self.roadLinker.linkConsequtiveRoadsWithNoBranches(roads)
        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-MergeAndTurns.xodr"
        odr.write_xml(xmlPath)


