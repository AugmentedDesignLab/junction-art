import unittest, os, math
from junctionart.junctions.StraightRoadBuilder import StraightRoadBuilder
from scipy.interpolate import CubicHermiteSpline
from junctionart.junctions.JunctionHarvester import JunctionHarvester
import numpy as np
import pyodrx as pyodrx, extensions
from junctionart.junctions.JunctionBuilder import JunctionBuilder
from junctionart.library.Configuration import Configuration
import junctions

from junctionart.junctions.Direction import CircularDirection
from junctionart.junctions.RoadLinker import RoadLinker
from junctionart.junctions.LaneSides import LaneSides
from junctionart.junctions.StandardCurveTypes import StandardCurveTypes


class test_ExtendedRoad(unittest.TestCase):
    def setUp(self):
        
        self.configuration = Configuration()
        self.roadBuilder = junctions.RoadBuilder()

        self.straightRoadBuilder = StraightRoadBuilder()
        self.roadLinker = RoadLinker()


    def test_getArcAngle(self):

        for _ in range(1, 10):
            for i in range(1, 10):
                inputAngle = (np.pi * i) / 10
                road = self.roadBuilder.createRandomCurve(0, inputAngle)

                if road.curveType == StandardCurveTypes.S:
                    continue

                outputAngle = road.getArcAngle()
                deviation = abs(inputAngle - outputAngle) * 100 / inputAngle

                print( f"curveType: {road.curveType} inputAngle: {math.degrees(inputAngle)} outputAngle: {math.degrees(outputAngle)} deviation: {deviation}")
                assert deviation < 50.0


    def test_getBorderDistanceOfLane(self):
        

        roads = []

        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=10, junction=-1, n_lanes_left=1, n_lanes_right=1))
        roads.append(self.straightRoadBuilder.createWithRightTurnLanesOnLeft(1, length = 10, n_lanes=1, junction=1,
                                                                                        isLeftTurnLane=True, 
                                                                                        isRightTurnLane=True,
                                                                                        numberOfRightTurnLanesOnLeft=2,
                                                                                        mergeLaneOnTheOppositeSideForInternalTurn=False))
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=4, n_lanes_right=2))
        self.roadLinker.linkConsecutiveRoadsWithNoBranches(roads)

        
        assert roads[0].getBorderDistanceOfLane(1, pyodrx.ContactPoint.start) == 3
        assert roads[0].getBorderDistanceOfLane(-1, pyodrx.ContactPoint.start) == 3
        assert roads[1].getBorderDistanceOfLane(1, pyodrx.ContactPoint.start) == 3
        assert roads[1].getBorderDistanceOfLane(2, pyodrx.ContactPoint.end) == 6
        assert roads[1].getBorderDistanceOfLane(3, pyodrx.ContactPoint.end) == 9
        assert roads[1].getBorderDistanceOfLane(4, pyodrx.ContactPoint.end) == 12
        assert roads[1].getBorderDistanceOfLane(-1, pyodrx.ContactPoint.start) == 3

        roads[1].updatePredecessorOffset(-1)

        odrName = "test_getBorderDistanceOfLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))


        

        xmlPath = f"output/test_getBorderDistanceOfLane.xodr"
        odr.write_xml(xmlPath)

        roads = []

        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=10, junction=-1, n_lanes_left=2, n_lanes_right=2))
        roads.append(self.straightRoadBuilder.createWithRightTurnLanesOnLeft(1, length = 10, n_lanes=2, junction=1,
                                                                                        isLeftTurnLane=True, 
                                                                                        isRightTurnLane=True,
                                                                                        numberOfRightTurnLanesOnLeft=2,
                                                                                        mergeLaneOnTheOppositeSideForInternalTurn=False))
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=5, n_lanes_right=3))
        self.roadLinker.linkConsecutiveRoadsWithNoBranches(roads)

        

        roads[1].updatePredecessorOffset(-2)

        odrName = "test_getBorderDistanceOfLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))


        

        xmlPath = f"output/test_getBorderDistanceOfLane.xodr"
        odr.write_xml(xmlPath)



    def test_getLanePosition(self):

        roads = []

        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=10, junction=-1, n_lanes_left=2, n_lanes_right=2))
        roads.append(self.straightRoadBuilder.createWithRightTurnLanesOnLeft(1, length = 10, n_lanes=2, junction=1,
                                                                                        isLeftTurnLane=True, 
                                                                                        isRightTurnLane=True,
                                                                                        numberOfRightTurnLanesOnLeft=2,
                                                                                        mergeLaneOnTheOppositeSideForInternalTurn=False))
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=5, n_lanes_right=3))
        self.roadLinker.linkConsecutiveRoadsWithNoBranches(roads)

        

        roads[1].updatePredecessorOffset(-2)

        odrName = "test_getBorderDistanceOfLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.printRoadPositions(odr)

        print(roads[0].getLanePosition(0, pyodrx.ContactPoint.end))
        print(roads[0].getLanePosition(1, pyodrx.ContactPoint.end))
        print(roads[0].getLanePosition(2, pyodrx.ContactPoint.end))

        positionLeftMost = roads[0].getLanePosition(2, pyodrx.ContactPoint.end)
        assert positionLeftMost[0] == 10.0
        assert positionLeftMost[1] == 6.0
        assert positionLeftMost[2] == 0
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))


