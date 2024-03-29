import unittest

import numpy as np
import os, dill
import pyodrx as pyodrx 
from junctionart.junctions.JunctionMerger import JunctionMerger
import junctionart.extensions as extensions
from junctionart.library.Configuration import Configuration
from junctionart.junctions.JunctionBuilder import JunctionBuilder
from junctionart.junctions.RoadBuilder import RoadBuilder
from junctionart.junctions.LaneBuilder import LaneBuilder

from junctionart.junctions.LaneLinker import LaneLinker
from junctionart.junctions.RoadLinker import RoadLinker
from junctionart.junctions.StraightRoadBuilder import StraightRoadBuilder


class test_LaneLinker(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()
        self.esminiPath = self.configuration.get("esminipath")
        self.roadBuilder = RoadBuilder()
        self.laneBuilder = LaneBuilder()
        self.laneLinker = LaneLinker()
        self.straightRoadBuilder = StraightRoadBuilder()
        self.roadLinker = RoadLinker()

    
    def test_normalRoadLinks(self):
        
        roads = []
        roads.append(self.straightRoadBuilder.create(0))
        roads.append(self.roadBuilder.curveBuilder.createSimple(1, np.pi/4, False, curvature = 0.2))
        roads.append(self.straightRoadBuilder.create(2))


        RoadLinker.createExtendedPredSuc(predRoad=roads[0], predCp=pyodrx.ContactPoint.end, sucRoad=roads[1], sucCP=pyodrx.ContactPoint.start)

        RoadLinker.createExtendedPredSuc(predRoad=roads[1], predCp=pyodrx.ContactPoint.end, sucRoad=roads[2], sucCP=pyodrx.ContactPoint.start)


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