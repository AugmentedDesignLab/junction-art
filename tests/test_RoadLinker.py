import unittest

import numpy as np
import os, dill, math
import pyodrx 
from junctions.JunctionMerger import JunctionMerger
import junctionart.extensions as extensions
from library.Configuration import Configuration
from junctions.JunctionBuilder import JunctionBuilder
from junctions.RoadBuilder import RoadBuilder
from junctions.LaneBuilder import LaneBuilder

from junctions.LaneLinker import LaneLinker

from junctions.StraightRoadBuilder import StraightRoadBuilder
from junctions.CurveRoadBuilder import CurveRoadBuilder

from junctions.RoadLinker import RoadLinker


class test_RoadLiner(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        self.esminiPath = self.configuration.get("esminipath")
        self.roadBuilder = RoadBuilder()
        self.laneBuilder = LaneBuilder()
        self.laneLinker = LaneLinker()
        self.straightRoadBuilder = StraightRoadBuilder()
        self.curveBuilder = CurveRoadBuilder()
        self.roadLinker = RoadLinker()

    

    def test_getAngleBetweenStraightRoads(self):
        roads = []
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, 10, n_lanes_left=1, n_lanes_right=1))
        connectionRoad = self.curveBuilder.create(1, np.pi / 4, isJunction=True, curvature=0.2, n_lanes=1)
        roads.append(connectionRoad)
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, 10, n_lanes_left=1, n_lanes_right=2))

        connectionRoad2 = self.curveBuilder.create(3, np.pi / 2, isJunction=True, curvature=0.1, n_lanes=1)
        roads.append(connectionRoad2)
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(4, 10, n_lanes_left=1, n_lanes_right=1))

        roads[0].addExtendedSuccessor(roads[1], 0, pyodrx.ContactPoint.start)

        roads[1].addExtendedPredecessor(roads[0], 0, pyodrx.ContactPoint.end)
        roads[1].addExtendedSuccessor(roads[2], 0, pyodrx.ContactPoint.start)

        roads[2].addExtendedPredecessor(roads[1], 0, pyodrx.ContactPoint.end)
        roads[2].addExtendedSuccessor(roads[3], 0, pyodrx.ContactPoint.start)

        roads[3].addExtendedPredecessor(roads[2], 0, pyodrx.ContactPoint.start)
        roads[3].addExtendedSuccessor(roads[4], 0, pyodrx.ContactPoint.start)

        roads[4].addExtendedPredecessor(roads[3], 0, pyodrx.ContactPoint.end)

        self.laneBuilder.createLanesForConnectionRoad(connectionRoad, roads[0], roads[2])
        self.laneBuilder.createLanesForConnectionRoad(connectionRoad2, roads[2], roads[4])

        
        odrName = "test_DifferentLaneConfigurations"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        print( math.degrees(self.roadLinker.getAngleBetweenStraightRoads(roads[0], roads[2])) )
        print( math.degrees(self.roadLinker.getAngleBetweenStraightRoads(roads[0], roads[4])) )
        print( math.degrees(self.roadLinker.getAngleBetweenStraightRoads(roads[2], roads[4])) )

        # xmlPath = f"output/test_DifferentLaneConfigurations.xodr"
        # odr.write_xml(xmlPath)



    def test_StartEnd(self):
        roads = []
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, 10, n_lanes_left=1, n_lanes_right=1))
        connectionRoad = self.curveBuilder.create(1, np.pi / 4, isJunction=True, curvature=0.1, n_lanes=1)
        roads.append(connectionRoad)
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, 10, n_lanes_left=1, n_lanes_right=1))


        roads[0].addExtendedSuccessor(roads[1], 0, pyodrx.ContactPoint.start)

        roads[1].addExtendedPredecessor(roads[0], 0, pyodrx.ContactPoint.start)
        roads[1].addExtendedSuccessor(roads[2], 0, pyodrx.ContactPoint.start)

        roads[2].addExtendedPredecessor(roads[1], 0, pyodrx.ContactPoint.end)

        self.laneBuilder.createLanesForConnectionRoad(connectionRoad, roads[0], roads[2])

        
        odrName = "test_StartEnd"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        print( math.degrees(self.roadLinker.getAngleBetweenStraightRoads(roads[0], roads[2])) )

        xmlPath = f"output/test_StartEnd.xodr"
        odr.write_xml(xmlPath)



    def test_fails(self):
        roads = []
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, 10, n_lanes_left=1, n_lanes_right=1))
        connectionRoad = self.curveBuilder.create(1, np.pi / 4, isJunction=True, curvature=0.2, n_lanes=1)
        roads.append(connectionRoad)
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, 10, n_lanes_left=1, n_lanes_right=2))

        connectionRoad2 = self.curveBuilder.create(3, np.pi / 2, isJunction=True, curvature=0.1, n_lanes=1)
        roads.append(connectionRoad2)
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(4, 10, n_lanes_left=1, n_lanes_right=3))

        roads[0].addExtendedSuccessor(roads[1], 0, pyodrx.ContactPoint.start)

        roads[1].addExtendedPredecessor(roads[0], 0, pyodrx.ContactPoint.end)
        roads[1].addExtendedSuccessor(roads[2], 0, pyodrx.ContactPoint.start)

        roads[2].addExtendedPredecessor(roads[1], 0, pyodrx.ContactPoint.end)
        roads[2].addExtendedSuccessor(roads[3], 0, pyodrx.ContactPoint.start)

        roads[3].addExtendedPredecessor(roads[2], 0, pyodrx.ContactPoint.start)
        roads[3].addExtendedSuccessor(roads[4], 0, pyodrx.ContactPoint.start)

        roads[4].addExtendedPredecessor(roads[3], 0, pyodrx.ContactPoint.end)

        self.laneBuilder.createLanesForConnectionRoad(connectionRoad, roads[0], roads[2])
        self.laneBuilder.createLanesForConnectionRoad(connectionRoad2, roads[2], roads[4])

        
        odrName = "test_DifferentLaneConfigurations"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        print( math.degrees(self.roadLinker.getAngleBetweenStraightRoads(roads[0], roads[2])) )
        print( math.degrees(self.roadLinker.getAngleBetweenStraightRoads(roads[0], roads[4])) )
        print( math.degrees(self.roadLinker.getAngleBetweenStraightRoads(roads[2], roads[4])) )

        # xmlPath = f"output/test_DifferentLaneConfigurations.xodr"
        # odr.write_xml(xmlPath)
