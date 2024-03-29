import unittest, os, math
from junctionart.junctions.StraightRoadBuilder import StraightRoadBuilder
from scipy.interpolate import CubicHermiteSpline
from junctionart.junctions.JunctionHarvester import JunctionHarvester
import numpy as np
import pyodrx as pyodrx
import junctionart.extensions as extensions
from junctionart.junctions.JunctionBuilder import JunctionBuilder
from junctionart.library.Configuration import Configuration
import junctionart.junctions

from junctionart.junctions.Direction import CircularDirection
from junctionart.junctions.RoadLinker import RoadLinker
from junctionart.junctions.LaneSides import LaneSides
from junctionart.junctions.StandardCurveTypes import StandardCurveTypes
from junctionart.junctions.ConnectionBuilder import ConnectionBuilder
from junctionart.junctions.CurveRoadBuilder import CurveRoadBuilder
from junctionart.junctions.AngleCurvatureMap import AngleCurvatureMap
from junctionart.junctions.StandardCurveTypes import StandardCurveTypes


class test_AngleCurvatureMap(unittest.TestCase):
    def setUp(self):
        
        self.configuration = Configuration()
        self.esminipath = self.configuration.get("esminipath")
        self.roadBuilder = junctions.RoadBuilder()

        self.straightRoadBuilder = StraightRoadBuilder()
        self.roadLinker = RoadLinker()
        self.connectionBuilder = ConnectionBuilder()
        self.curveRoadBuilder = CurveRoadBuilder()


    def test_getCurvatureForAngleAndLength(self):
        

        numberofLanes = 5
        laneOffset = 3
        # angle = np.pi * .75
        # angle = np.pi * (5/6)
        # length = 15
        
        # maxCurve = AngleCurvatureMap.getMaxCurvatureMaxRoadWidth(angle, numberofLanes * laneOffset)
        # curve = AngleCurvatureMap.getCurvatureForAngleBetweenRoadAndLength(angle, length, StandardCurveTypes.Simple) 

        # # curve = 0.066666667

        # print(f"max curve {maxCurve}, current curve {curve}")

        # roads = []
        # roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=10, junction=-1, n_lanes_left=numberofLanes, n_lanes_right=numberofLanes))
        # # roads.append(self.curveRoadBuilder.createSimpleCurveWithLongArc(1, angleBetweenEndpoints = angle, curvature=curve, isJunction=True, n_lanes=numberofLanes))
        # roads.append(self.curveRoadBuilder.createSimple(1, angleBetweenEndpoints = angle, curvature=curve, isJunction=True, n_lanes=numberofLanes))
        # roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=numberofLanes, n_lanes_right=numberofLanes))
        
        # RoadLinker.createExtendedPredSuc(predRoad=roads[0], predCp=pyodrx.ContactPoint.end, sucRoad=roads[1], sucCP=pyodrx.ContactPoint.start)
        # RoadLinker.createExtendedPredSuc(predRoad=roads[1], predCp=pyodrx.ContactPoint.end, sucRoad=roads[2], sucCP=pyodrx.ContactPoint.start)

        # odrName = "test_createSingleLaneConnectionRoad"
        # odr = extensions.createOdrByPredecessor(odrName, roads, [])
        # # extensions.printRoadPositions(odr)

        # road = roads[1]
        # print(f"{road.id} has length {road.planview.get_total_length()}")

        # # for geom in road.planview._adjusted_geometries:
        # #     print(geom.length)

        # assert round(road.planview.get_total_length(), 0) == length       
        # extensions.view_road(odr, os.path.join('..', self.esminipath))


        angle = 0.5
        while angle < np.pi:

            length = 100

            while length > 0:
                
                curve = AngleCurvatureMap.getCurvatureForAngleBetweenRoadAndLength(angle, length, StandardCurveTypes.Simple) 
                roads = []
                curve = AngleCurvatureMap.getCurvatureForAngleBetweenRoadAndLength(angle, length, StandardCurveTypes.Simple) 
                roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=10, junction=-1, n_lanes_left=numberofLanes, n_lanes_right=numberofLanes))
                roads.append(self.curveRoadBuilder.createSimple(1, angleBetweenEndpoints = angle, curvature=curve, isJunction=True, n_lanes=numberofLanes))
                roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=numberofLanes, n_lanes_right=numberofLanes))
                
                RoadLinker.createExtendedPredSuc(predRoad=roads[0], predCp=pyodrx.ContactPoint.end, sucRoad=roads[1], sucCP=pyodrx.ContactPoint.start)
                RoadLinker.createExtendedPredSuc(predRoad=roads[1], predCp=pyodrx.ContactPoint.end, sucRoad=roads[2], sucCP=pyodrx.ContactPoint.start)
                odrName = "test_createSingleLaneConnectionRoad"
                odr = extensions.createOdrByPredecessor(odrName, roads, [])
                road = roads[1]

                assert round(road.planview.get_total_length(), 0) == length   
                   
                curve = AngleCurvatureMap.getCurvatureForAngleBetweenRoadAndLength(angle, length, StandardCurveTypes.Simple) 
                roads = []
                curve = AngleCurvatureMap.getCurvatureForAngleBetweenRoadAndLength(angle, length, StandardCurveTypes.Simple) 
                roads.append(self.curveRoadBuilder.createSimpleCurveWithLongArc(1, angleBetweenEndpoints = angle, curvature=curve, isJunction=True, n_lanes=numberofLanes))
                roads.append(self.curveRoadBuilder.createSimple(1, angleBetweenEndpoints = angle, curvature=curve, isJunction=True, n_lanes=numberofLanes))
                roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=numberofLanes, n_lanes_right=numberofLanes))
                
                RoadLinker.createExtendedPredSuc(predRoad=roads[0], predCp=pyodrx.ContactPoint.end, sucRoad=roads[1], sucCP=pyodrx.ContactPoint.start)
                RoadLinker.createExtendedPredSuc(predRoad=roads[1], predCp=pyodrx.ContactPoint.end, sucRoad=roads[2], sucCP=pyodrx.ContactPoint.start)
                odrName = "test_createSingleLaneConnectionRoad"
                odr = extensions.createOdrByPredecessor(odrName, roads, [])
                road = roads[1]

                assert round(road.planview.get_total_length(), 0) == length      


                length -= 10

            angle += 0.25


    def test_getMaxCurvatureMaxRoadWidth(self):
        
        roads = []

        numberofLanes = 1
        laneOffset = 3
        angle = np.pi * .75
        
        maxCurve = AngleCurvatureMap.getMaxCurvatureAgainstMaxRoadWidth(angle, numberofLanes * laneOffset)

        curve = maxCurve * 1.1

        print(f"max curve {maxCurve}, current curve {curve}")

        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=10, junction=-1, n_lanes_left=numberofLanes, n_lanes_right=numberofLanes))
        roads.append(self.curveRoadBuilder.createSimpleCurveWithLongArc(1, angleBetweenEndpoints = angle, curvature=curve, isJunction=True, n_lanes=numberofLanes))
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=numberofLanes, n_lanes_right=numberofLanes))
        
        RoadLinker.createExtendedPredSuc(predRoad=roads[0], predCp=pyodrx.ContactPoint.end, sucRoad=roads[1], sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=roads[1], predCp=pyodrx.ContactPoint.end, sucRoad=roads[2], sucCP=pyodrx.ContactPoint.start)

        odrName = "test_createSingleLaneConnectionRoad"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        # extensions.printRoadPositions(odr)

        road = roads[1]
        print(f"{road.id} has length {road.planview.get_total_length()}")

        for geom in road.planview._adjusted_geometries:
            print(geom.length)
        
        extensions.view_road(odr, os.path.join('..', self.esminipath))

    
    def test_getLength(self):

        angleBetweenEndpoints = 1.5708
        curvature = 0.333333
        curveType = StandardCurveTypes.Simple
        currentLength = AngleCurvatureMap.getLength(angleBetweenEndpoints, curvature, curveType)

        print(f"test length: {currentLength}")

        numberofLanes = 5
        laneOffset = 3
        
        angle = angleBetweenEndpoints
        length = currentLength
        
        maxCurve = AngleCurvatureMap.getCurvatureForAngleBetweenRoadAndLength(angle, numberofLanes * laneOffset, curveType=curveType)
        curve = AngleCurvatureMap.getCurvatureForAngleBetweenRoadAndLength(angle, length, curveType=curveType) 

        # curve = 0.066666667

        print(f"max curve {maxCurve}, current curve {curve}")

        roads = []
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=10, junction=-1, n_lanes_left=numberofLanes, n_lanes_right=numberofLanes))
        # roads.append(self.curveRoadBuilder.createSimpleCurveWithLongArc(1, angleBetweenEndpoints = angle, curvature=curve, isJunction=True, n_lanes=numberofLanes))
        roads.append(self.curveRoadBuilder.createSimple(1, angleBetweenEndpoints = angle, curvature=curve, isJunction=True, n_lanes=numberofLanes))
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=numberofLanes, n_lanes_right=numberofLanes))
        
        RoadLinker.createExtendedPredSuc(predRoad=roads[0], predCp=pyodrx.ContactPoint.end, sucRoad=roads[1], sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=roads[1], predCp=pyodrx.ContactPoint.end, sucRoad=roads[2], sucCP=pyodrx.ContactPoint.start)

        odrName = "test_createSingleLaneConnectionRoad"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        # extensions.printRoadPositions(odr)

        road = roads[1]
        print(f"{road.id} has length {road.planview.get_total_length()}")

        # for geom in road.planview._adjusted_geometries:
        #     print(geom.length)

        assert round(road.planview.get_total_length(), 0) == round(length,0)