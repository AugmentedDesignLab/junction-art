import unittest
import pyodrx, extensions
from library.Configuration import Configuration
import numpy as np
from junctions.RoadBuilder import RoadBuilder
from junctions.JunctionBuilder import JunctionBuilder
from junctions.AngleCurvatureMap import AngleCurvatureMap
import math


class test_NonOverlappingCurve(unittest.TestCase):

    def setUp(self):
        self.roadBuilder = RoadBuilder()
        self.junctionBuilder = JunctionBuilder()
        self.configuration = Configuration()
        self.angleCurvatureMap = AngleCurvatureMap()
        self.esminiPath = self.configuration.get("esminipath")


    def test_NonOverlappingCurve(self):
        angle = 120
        numberofLanes = 20
        laneOffset = 3
        curve, angle = self.angleCurvatureMap.getCurvatureForNonOverlappingRoads(angle, numberofLanes, laneOffset)
        roads = []
        roads.append(pyodrx.create_straight_road(0, 100,  n_lanes=numberofLanes, lane_offset=laneOffset))
        roads.append(self.roadBuilder.createSimpleCurveWithLongArcWithLaneNumberandOffset(1, angle, False, curvature = curve, _n_lanes = numberofLanes, _lane_offset=laneOffset))
        roads.append(pyodrx.create_straight_road(2, 100, n_lanes=numberofLanes, lane_offset=laneOffset))

        roads[0].add_successor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.start)

        roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
        roads[1].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

        roads[2].add_predecessor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.end)

        odrName = "curve_test"
        odr = extensions.createOdr(odrName, roads, [])
        extensions.view_road(odr, self.esminiPath)
        
        


