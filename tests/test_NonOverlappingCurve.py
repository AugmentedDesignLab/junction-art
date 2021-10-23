import unittest
import pyodrx as pyodrx
import junctionart.extensions as extensions
from junctionart.library.Configuration import Configuration
import numpy as np
from junctionart.junctions.RoadBuilder import RoadBuilder
from junctionart.junctions.JunctionBuilder import JunctionBuilder
from junctionart.junctions.AngleCurvatureMap import AngleCurvatureMap
import math


class test_NonOverlappingCurve(unittest.TestCase):

    def setUp(self):
        self.roadBuilder = RoadBuilder()
        self.junctionBuilder = JunctionBuilder()
        self.configuration = Configuration()
        self.angleCurvatureMap = AngleCurvatureMap()
        self.esminiPath = self.configuration.get("esminipath")


    def test_NonOverlappingCurve(self):
        numberofLanes = 10
        laneOffset = 3
        # angle = 120
        # curve, angle = AngleCurvatureMap.getCurvatureForNonOverlappingRoads(angle, numberofLanes, laneOffset)

        angle = np.pi * 0.75 
        # curve, angle = AngleCurvatureMap.getCurvatureForNonOverlappingRoads(angle, numberofLanes, laneOffset)
        curve = AngleCurvatureMap.getMaxCurvatureAgainstMaxRoadWidth(angle, numberofLanes * laneOffset)
        roads = []
        roads.append(pyodrx.create_straight_road(0, 50,  n_lanes=numberofLanes, lane_offset=laneOffset))
        roads.append(self.roadBuilder.createSimpleCurveWithLongArcWithLaneNumberandOffset(1, angle, False, curvature = curve, _n_lanes = numberofLanes, _lane_offset=laneOffset))
        roads.append(pyodrx.create_straight_road(2, 50, n_lanes=numberofLanes, lane_offset=laneOffset))

        roads[0].add_successor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.start)

        roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
        roads[1].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

        roads[2].add_predecessor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.end)

        odrName = "curve_test"
        odr = extensions.createOdr(odrName, roads, [])
        extensions.view_road(odr, self.esminiPath)
        


    def test_getCurvatureForAngleAndLength(self):
        numberofLanes = 10
        laneOffset = 3
        # angle = 120
        # curve, angle = AngleCurvatureMap.getCurvatureForNonOverlappingRoads(angle, numberofLanes, laneOffset)

        angle = np.pi * 1.2
        length = 20
        # curve, angle = AngleCurvatureMap.getCurvatureForNonOverlappingRoads(angle, numberofLanes, laneOffset)
        maxCurve = AngleCurvatureMap.getMaxCurvatureAgainstMaxRoadWidth(angle, numberofLanes * laneOffset)
        curve = AngleCurvatureMap.getCurvatureForAngleAndLength(angle, length)

        print(f"max curve {maxCurve}, current curve {curve}")
        roads = []
        roads.append(pyodrx.create_straight_road(0, 50,  n_lanes=numberofLanes, lane_offset=laneOffset))
        roads.append(self.roadBuilder.createSimpleCurveWithLongArcWithLaneNumberandOffset(1, angle, False, curvature = curve, _n_lanes = numberofLanes, _lane_offset=laneOffset))
        roads.append(pyodrx.create_straight_road(2, 50, n_lanes=numberofLanes, lane_offset=laneOffset))

        roads[0].add_successor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.start)

        roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
        roads[1].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

        roads[2].add_predecessor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.end)

        odrName = "curve_test"
        odr = extensions.createOdr(odrName, roads, [])
        extensions.view_road(odr, self.esminiPath)
        
        


