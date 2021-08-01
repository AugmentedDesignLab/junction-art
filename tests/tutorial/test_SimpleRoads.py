import unittest
from junctions.StraightRoadBuilder import StraightRoadBuilder
import extensions
import os
from library.Configuration import Configuration
from junctions.RoadLinker import RoadLinker
from junctions.JunctionBuilder import JunctionBuilder
from junctions.LaneBuilder import LaneBuilder
from junctions.CurveRoadBuilder import CurveRoadBuilder
from junctions.StandardCurvatures import StandardCurvature
from junctions.RoadBuilder import RoadBuilder
from extensions.CountryCodes import CountryCodes
from junctions.ODRHelper import ODRHelper
import pyodrx
import numpy as np

class test_SimpleRoads(unittest.TestCase):

    def setUp(self) -> None:
        print("\nsetUp is called")
        self.configuration = Configuration()
        self.straightbuilder = StraightRoadBuilder()
        self.junctionBuilder = JunctionBuilder()
        self.laneBuilder = LaneBuilder()
        self.curveBuilder = CurveRoadBuilder()
        self.roadBuilder = RoadBuilder()


    def test_oneStraightRoad(self):

        print("\ntest_oneStraightRoad is called")

        # 1. create logical descriptions for each road in our network
        for _ in range(5):
            road = self.straightbuilder.createRandom(roadId=1, minLanePerSide=1, maxLanePerSide=1) # logical description of a road.

            # 2. place the roads into a map
            odr = extensions.createOdrByPredecessor("First simple road network with one straight road only", [road], [])

            
            xmlPath = f"output/test_straightRoads.xodr"
            odr.write_xml(xmlPath)
            
            extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))



    def test_2Roads(self):
        # 1. create logical descriptions for each road in our network
        road1 = self.straightbuilder.createRandom(roadId=1, turns=True) # logical description of a road.
        road2 = self.straightbuilder.createRandom(roadId=2, merges=True) # logical description of a road.

      
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
        road1 = self.straightbuilder.createRandom(roadId=1, turns=True) # logical description of a road.
        road2 = self.straightbuilder.createRandom(roadId=2, merges=True) # logical description of a road.

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



    
    def test_assignment1(self):

        road1 = self.straightbuilder.createRandom(roadId=1, minLanePerSide=2, maxLanePerSide=2)
        road2 = self.curveBuilder.create(2, angleBetweenEndpoints=np.pi/3, n_lanes=2, curvature=.1)
        # road2 = self.curveBuilder.createCurveByLength(2, length=20, curvature=StandardCurvature.Sharp.value)
        road3 = self.straightbuilder.createRandom(roadId=3, minLanePerSide=2, maxLanePerSide=2)
        
        # define successor predecessor relationships
        RoadLinker.createExtendedPredSuc(predRoad=road1, predCp=pyodrx.ContactPoint.end, sucRoad=road2, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=road2, predCp=pyodrx.ContactPoint.end, sucRoad=road3, sucCP=pyodrx.ContactPoint.start)


        roads = [road1, road2]
        roads = [road1, road2, road3]
        
        # 3. place the roads into a map
        odr = extensions.createOdrByPredecessor("First simple road network with one straight road only", roads, [])

        xmlPath = f"output/test_assignment1.xodr"
        odr.write_xml(xmlPath)
        
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))


    def test_D(self):
        road1 = self.straightbuilder.createRandom(roadId=1, minLanePerSide=1, maxLanePerSide=1, length=1)
        road2 = self.curveBuilder.create(2, angleBetweenEndpoints=0.01, n_lanes=1, curvature=.07)
        road3 = self.straightbuilder.createRandom(roadId=3, minLanePerSide=1, maxLanePerSide=1, length=1)
        road4 = self.curveBuilder.create(4, angleBetweenEndpoints=np.pi/2, n_lanes=1, curvature=.6)
        road5 = self.straightbuilder.createRandom(roadId=5, minLanePerSide=1, maxLanePerSide=1, length=30)


        # define successor predecessor relationships
        RoadLinker.createExtendedPredSuc(predRoad=road1, predCp=pyodrx.ContactPoint.end, sucRoad=road2, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=road2, predCp=pyodrx.ContactPoint.end, sucRoad=road3, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=road3, predCp=pyodrx.ContactPoint.end, sucRoad=road4, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=road4, predCp=pyodrx.ContactPoint.end, sucRoad=road5, sucCP=pyodrx.ContactPoint.start)


        roads = [road1, road2, road3, road4, road5]
        
        odr = extensions.createOdrByPredecessor("First simple road network with one straight road only", roads, [], countryCode=CountryCodes.US)
        

        road6 = self.roadBuilder.getConnectionRoadBetween(6, road1=road5, road2=road1, cp1=pyodrx.ContactPoint.end, cp2=pyodrx.ContactPoint.start)

        # define successor predecessor relationships
        RoadLinker.createExtendedPredSuc(predRoad=road5, predCp=pyodrx.ContactPoint.end, sucRoad=road6, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=road6, predCp=pyodrx.ContactPoint.end, sucRoad=road1, sucCP=pyodrx.ContactPoint.start)

        roads.append(road6)
        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)

        xmlPath = f"output/test_assignment1.xodr"
        odr.write_xml(xmlPath)
        
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))

    
    
    def test_D_rotated(self):
        road1 = self.straightbuilder.createRandom(roadId=1, minLanePerSide=1, maxLanePerSide=1, length=1)
        road2 = self.curveBuilder.create(2, angleBetweenEndpoints=0.01, n_lanes=1, curvature=.07)
        road3 = self.straightbuilder.createRandom(roadId=3, minLanePerSide=1, maxLanePerSide=1, length=1)
        road4 = self.curveBuilder.create(4, angleBetweenEndpoints=np.pi/2, n_lanes=1, curvature=.6)
        road5 = self.straightbuilder.createRandom(roadId=5, minLanePerSide=1, maxLanePerSide=1, length=30)


        # define successor predecessor relationships
        RoadLinker.createExtendedPredSuc(predRoad=road1, predCp=pyodrx.ContactPoint.end, sucRoad=road2, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=road2, predCp=pyodrx.ContactPoint.end, sucRoad=road3, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=road3, predCp=pyodrx.ContactPoint.end, sucRoad=road4, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=road4, predCp=pyodrx.ContactPoint.end, sucRoad=road5, sucCP=pyodrx.ContactPoint.start)


        roads = [road1, road2, road3, road4, road5]
        
        odr = extensions.createOdrByPredecessor("First simple road network with one straight road only", roads, [], countryCode=CountryCodes.US)
        

        road6 = self.roadBuilder.getConnectionRoadBetween(6, road1=road5, road2=road1, cp1=pyodrx.ContactPoint.end, cp2=pyodrx.ContactPoint.start)

        # define successor predecessor relationships
        RoadLinker.createExtendedPredSuc(predRoad=road5, predCp=pyodrx.ContactPoint.end, sucRoad=road6, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=road6, predCp=pyodrx.ContactPoint.end, sucRoad=road1, sucCP=pyodrx.ContactPoint.start)

        roads.append(road6)
        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)

        ODRHelper.transform(odr, startX=100, startY=200, heading=-np.pi/4)

        xmlPath = f"output/test_assignment1.xodr"
        odr.write_xml(xmlPath)
        
        extensions.view_road(odr, os.path.join('..',self.configuration.get("esminipath")))
