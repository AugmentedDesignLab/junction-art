import unittest

import numpy as np
import os, dill
import pyodrx 
from junctions.JunctionMerger import JunctionMerger
import extensions
from library.Configuration import Configuration
from junctions.JunctionBuilder import JunctionBuilder
from junctions.RoadBuilder import RoadBuilder
from junctions.LaneBuilder import LaneBuilder

from junctions.LaneLinker import LaneLinker
from junctions.StraightRoadBuilder import StraightRoadBuilder


class test_LaneLinker(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        self.esminiPath = self.configuration.get("esminipath")
        self.roadBuilder = RoadBuilder()
        self.laneBuilder = LaneBuilder()
        self.laneLinker = LaneLinker()
        self.straightRoadBuilder = StraightRoadBuilder()

    
    def test_normalRoadLinks(self):
        
        roads = []
        roads.append(pyodrx.create_straight_road(0, 10))
        roads.append(self.roadBuilder.createSimpleCurve(1, np.pi/4, False, curvature = 0.2))
        roads.append(pyodrx.create_straight_road(2, 10))


        roads[0].add_successor(pyodrx.ElementType.road,1, pyodrx.ContactPoint.start)

        roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.end)
        # roads[1].add_predecessor(pyodrx.ElementType.road,0,pyodrx.ContactPoint.start)
        roads[1].add_successor(pyodrx.ElementType.road,2,pyodrx.ContactPoint.start)

        roads[2].add_predecessor(pyodrx.ElementType.road,1,pyodrx.ContactPoint.end)


        odrName = "test_connectionRoad"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        # self.laneBuilder.addRightTurnLaneUS(roads[0], 3)
        # self.laneBuilder.addRightLaneUS(roads[1])

        # odr.resetAndReadjust(byPredecessor=True)

        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))


    def test_DifferentCPs(self):

        # same cps
        roads = []
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=20, junction=-1, n_lanes_left=2, n_lanes_right=1))
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(1, length=10, junction=-1, n_lanes_left=1, n_lanes_right=2))

        roads[0].addExtendedSuccessor(roads[1], 0, pyodrx.ContactPoint.start)
        roads[1].addExtendedPredecessor(roads[0], 0, pyodrx.ContactPoint.start)

        odrName = "test_DifferentCPs1"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        

        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_DifferentCPs1.xodr"
        odr.write_xml(xmlPath)

        # same cps 2
        roads = []
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=20, junction=-1, n_lanes_left=2, n_lanes_right=1))
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(1, length=10, junction=-1, n_lanes_left=2, n_lanes_right=1))

        roads[0].addExtendedSuccessor(roads[1], 0, pyodrx.ContactPoint.start)
        roads[1].addExtendedPredecessor(roads[0], 0, pyodrx.ContactPoint.end)

        odrName = "test_DifferentCPs2"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        

        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_DifferentCPs2.xodr"
        odr.write_xml(xmlPath)