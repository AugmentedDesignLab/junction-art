import unittest
from junctions.StraightRoadBuilder import StraightRoadBuilder
import extensions
import os
from library.Configuration import Configuration
from junctions.RoadLinker import RoadLinker
from junctions.JunctionBuilder import JunctionBuilder
from junctions.LaneBuilder import LaneBuilder
from junctions.CurveRoadBuilder import CurveRoadBuilder
import pyodrx
import numpy as np

class test_SimpleRoads(unittest.TestCase):

    def setUp(self) -> None:
        print("\nsetUp is called")
        self.configuration = Configuration()
        self.builder = StraightRoadBuilder()
        self.junctionBuilder = JunctionBuilder()
        self.laneBuilder = LaneBuilder()
        self.curveBuilder = CurveRoadBuilder()


    def test_oneStraightRoad(self):

        print("\ntest_oneStraightRoad is called")

        # 1. create logical descriptions for each road in our network
        road = self.builder.createRandom(roadId=1) # logical description of a road.

        # 2. place the roads into a map
        odr = extensions.createOdrByPredecessor("First simple road network with one straight road only", [road], [])

        
        xmlPath = f"output/test_straightRoads.xodr"
        odr.write_xml(xmlPath)
        
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))

    def test_2Roads(self):
        # 1. create logical descriptions for each road in our network
        road1 = self.builder.createRandom(roadId=1, turns=True) # logical description of a road.
        road2 = self.builder.createRandom(roadId=2, merges=True) # logical description of a road.

      
        # define successor predecessor relationships

        road2.addExtendedPredecessor(road1, 0, cp=pyodrx.ContactPoint.end)
        road1.addExtendedSuccessor(road2, 0, cp=pyodrx.ContactPoint.start)

        # 3. place the roads into a map
        odr = extensions.createOdrByPredecessor("First simple road network with one straight road only", [road1, road2], [])

        xmlPath = f"output/test_3Roads.xodr"
        odr.write_xml(xmlPath)
        
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))

        pass


    def test_3Roads(self):
        # 1. create logical descriptions for each road in our network
        road1 = self.builder.createRandom(roadId=1, turns=True) # logical description of a road.
        road2 = self.builder.createRandom(roadId=2, merges=True) # logical description of a road.

        # solve reference line to connect
        # road3 = self.junctionBuilder.createConnectionFor2Roads(nextRoadId=3, road1=road1, road2=road2, junction=None, cp1=pyodrx.ContactPoint.end, cp2=pyodrx.ContactPoint.start)
        # solve diff lane configurations at endpoints
        road3 = self.curveBuilder.create(roadId=3, angleBetweenEndpoints=np.pi/1.5)

        # define successor predecessor relationships
        RoadLinker.createExtendedPredSuc(predRoad=road1, predCp=pyodrx.ContactPoint.end, sucRoad=road3, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=road3, predCp=pyodrx.ContactPoint.end, sucRoad=road2, sucCP=pyodrx.ContactPoint.start)

        # creates 3 lane sections inside the road to have different lane configurations.
        self.laneBuilder.createLanesForConnectionRoad(road3, road1, road2)

        # 3. place the roads into a map
        odr = extensions.createOdrByPredecessor("First simple road network with one straight road only", [road1, road3, road2], [])

        xmlPath = f"output/test_3Roads.xodr"
        odr.write_xml(xmlPath)
        
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))

        pass


