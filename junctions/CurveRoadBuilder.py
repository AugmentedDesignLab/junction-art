import numpy as np
import os
import pyodrx
import extensions
import math

from junctions.LaneSides import LaneSides
from junctions.StandardCurvatures import StandardCurvature
from junctions.StandardCurveTypes import StandardCurveTypes
from extensions.ExtendedRoad import ExtendedRoad
from extensions.ExtendedPlanview import ExtendedPlanview
from scipy.interpolate import CubicHermiteSpline

from junctions.RoadSeries import RoadSeries
from junctions.Direction import CircularDirection
from junctions.Geometry import Geometry
from junctions.LaneBuilder import LaneBuilder
from extensions.CountryCodes import CountryCodes
import extensions


class CurveRoadBuilder:

    def __init__(self, country=CountryCodes.US):
        self.STD_ROADMARK = pyodrx.RoadMark(pyodrx.RoadMarkType.solid, 0.2, rule=pyodrx.MarkRule.no_passing)
        self.STD_START_CLOTH = 1/1000000000
        self.country = country
        self.laneBuilder = LaneBuilder()
        pass


    def getJunctionSelection(self, isJunction):
        if isJunction:
            return 1
        return -1
    
    def createPVForArcWithCloths(self, arcCurvature, arcAngle, clothAngle, clothCurvatureStart = None, clothCurvatureEnd = None):
        """[summary]

        Args:
            arcCurvature ([type]): [description]
            arcAngle ([type]): [description]
            clothAngle ([type]): [description]
            clothCurvatureStart ([type], optional): [description]. Defaults to None.
            clothCurvatureEnd ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """

        if clothCurvatureStart is None:
            clothCurvatureStart = self.STD_START_CLOTH
        if clothCurvatureEnd is None:
            clothCurvatureEnd = self.STD_START_CLOTH
        
        pv = extensions.ExtendedPlanview()

        spiral1 = extensions.ExtendedSpiral(clothCurvatureStart, arcCurvature, angle=clothAngle)
        arc = pyodrx.Arc(arcCurvature, angle=arcAngle )
        spiral2 = extensions.ExtendedSpiral(arcCurvature, clothCurvatureEnd, angle=clothAngle)

        pv.add_geometry(spiral1)
        pv.add_geometry(arc)
        pv.add_geometry(spiral2)

        return pv


    def create(self, roadId, angleBetweenEndpoints, isJunction = False, curvature = StandardCurvature.Medium.value, curveType=StandardCurveTypes.Simple,
                    n_lanes=1, lane_offset=3, 
                    laneSides=LaneSides.BOTH,
                    isLeftTurnLane=False,
                    isRightTurnLane=False,
                    isLeftMergeLane=False,
                    isRightMergeLane=False
                    ):

        if curveType is StandardCurveTypes.Simple:
            return self.createSimple(roadId, angleBetweenEndpoints, isJunction, curvature, 
                                    isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
                                    isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane)
        elif curveType is StandardCurveTypes.LongArc:
            return self.createSimpleCurveWithLongArc(roadId, angleBetweenEndpoints, isJunction, curvature)
        elif curveType is StandardCurveTypes.S:
            return self.createS(roadId, angleBetweenEndpoints, isJunction, curvature)
        else:
            error = f"Unkown curveType {curveType} or not supported for random creation"
            raise Exception(error)


    def createSimple(self, roadId, angleBetweenEndpoints, isJunction = False, curvature = StandardCurvature.Medium.value,
                            n_lanes=1, lane_offset=3, 
                            laneSides=LaneSides.BOTH,
                            isLeftTurnLane=False,
                            isRightTurnLane=False,
                            isLeftMergeLane=False,
                            isRightMergeLane=False
                            ):

        junction = extensions.getJunctionSelection(isJunction)
        totalRotation = np.pi - angleBetweenEndpoints
        arcAngle = np.pi / 10000000
        clothAngle = totalRotation / 2
        
        return self.createCurveGeoAndLanes(roadId, isJunction, curvature, arcAngle, clothAngle, n_lanes, lane_offset, laneSides, 
                                            isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane)

    def createCurveGeoAndLanes(self, roadId, isJunction, curvature, arcAngle, clothAngle, n_lanes, lane_offset, 
                                
                                laneSides=LaneSides.BOTH,
                                isLeftTurnLane=False,
                                isRightTurnLane=False,
                                isLeftMergeLane=False,
                                isRightMergeLane=False):

        
        junction = extensions.getJunctionSelection(isJunction)

        pv = self.createPVForArcWithCloths(curvature, arcAngle, clothAngle)
        length = pv.getTotalLength()



        laneSections = self.laneBuilder.getStandardLanes(n_lanes, lane_offset, laneSides,
                                                            roadLength=length, 
                                                            isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
                                                            isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane)

        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction, curveType=StandardCurveTypes.LongArc)
        return road

    
    def createSimpleCurveWithLongArc(self, roadId, angleBetweenEndpoints, isJunction = False, curvature = StandardCurvature.Medium.value,
                            n_lanes=1, lane_offset=3, 
                            laneSides=LaneSides.BOTH,
                            isLeftTurnLane=False,
                            isRightTurnLane=False,
                            isLeftMergeLane=False,
                            isRightMergeLane=False
                            ): 
        
        junction = extensions.getJunctionSelection(isJunction)

        totalRotation = np.pi - angleBetweenEndpoints

        # most of the angleBetweenEndpoints should be assigned to the Arc
        arcAngle = totalRotation * 0.9 # main curve
        clothAngle = (totalRotation * 0.1) / 2 # curve more.

        return self.createCurveGeoAndLanes( roadId, isJunction, curvature, arcAngle, clothAngle, n_lanes, lane_offset, laneSides, 
                                            isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane)


    
    def createS(self, roadId, angleBetweenEndpoints, isJunction = False, curvature = StandardCurvature.Medium.value,
                            n_lanes=1, lane_offset=3, 
                            laneSides=LaneSides.BOTH,
                            isLeftTurnLane=False,
                            isRightTurnLane=False,
                            isLeftMergeLane=False,
                            isRightMergeLane=False
                            ): 
        """Here the angleBetweenEndpoints are used for the first road and S mid point, and S mid point and Second road

        Args:
            roadId ([type]): [description]
            angleBetweenEndpoints ([type]): used for the first road and S mid point, and S mid point and Second road. Use negative angles for interesting Ss
            isJunction (bool, optional): [description]. Defaults to False.
            curvature ([type], optional): [description]. Defaults to StandardCurvature.Medium.value.

        Returns:
            [type]: [description]
        """
        
        junction = extensions.getJunctionSelection(isJunction)

        totalRotation = np.pi - angleBetweenEndpoints

        # most of the angleBetweenEndpoints should be assigned to the Arc
        arcAngle = totalRotation * 0.9
        clothAngle = (totalRotation * 0.1) / 2 # curve more.

        arc_curv = curvature 
        arc_angle = arcAngle 
        cloth_angle = clothAngle 
        cloth_start = self.STD_START_CLOTH
        

        pv = ExtendedPlanview()
        # adjust sign if angle is negative
        if cloth_angle < 0 and  arc_curv > 0:

            cloth_angle = -cloth_angle
            arc_curv = -arc_curv
            cloth_start = -cloth_start
            arc_angle = -arc_angle 

        # we are changing the second half of the S to have different arc angle and curvature.
        multiplier = np.random.choice(9) / 10
        arc_angle2 = arc_angle - arc_angle * multiplier
        arc_curv2 = -(arc_curv + arc_curv * multiplier) # the angle needs to be opposite for the second half.
        
        # create geometries
        spiral1 = extensions.ExtendedSpiral(cloth_start, arc_curv, angle=cloth_angle)
        arc = pyodrx.Arc(arc_curv, angle=arc_angle )
        arc2 = pyodrx.Arc(arc_curv2, angle = -arc_angle2)
        spiral2 = extensions.ExtendedSpiral(-arc_curv, cloth_start, angle= -cloth_angle)

        pv.add_geometry(spiral1)
        pv.add_geometry(arc)
        pv.add_geometry(arc2)
        pv.add_geometry(spiral2)

        length = pv.getTotalLength()



        laneSections = self.laneBuilder.getStandardLanes(n_lanes, lane_offset, laneSides,
                                                            roadLength=length, 
                                                            isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
                                                            isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane)

        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction, curveType=StandardCurveTypes.S)
        return road

    
    def createCurveByLength(self, roadId, length, isJunction = False, curvature = StandardCurvature.Medium.value,
                    n_lanes=1, lane_offset=3, 
                    laneSides=LaneSides.BOTH,
                    isLeftTurnLane=False,
                    isRightTurnLane=False,
                    isLeftMergeLane=False,
                    isRightMergeLane=False):

        junction = self.getJunctionSelection(isJunction)

        pv = ExtendedPlanview()
        arc = pyodrx.Arc(curvature, length=length )
        pv.add_geometry(arc)

        length = pv.getTotalLength()



        laneSections = self.laneBuilder.getStandardLanes(n_lanes, lane_offset, laneSides,
                                                            roadLength=length, 
                                                            isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
                                                            isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane)

        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction, curveType=StandardCurveTypes.LongArc)
        return road



    def createParamPoly3(self, roadId, isJunction=False, 
                    au=0,bu=20,cu=20,du= 10,
                    av=0,bv=2,cv=20,dv= 10,
                    prange='normalized',
                    length=None,
                    n_lanes=1,
                    lane_offset=3,
                    laneSides=LaneSides.BOTH,
                    isLeftTurnLane=False,
                    isRightTurnLane=False,
                    isLeftMergeLane=False,
                    isRightMergeLane=False):

        junction = self.getJunctionSelection(isJunction)

        pv = ExtendedPlanview()
        
        poly = pyodrx.ParamPoly3(au,bu,cu,du,av,bv,cv,dv,prange,length)
        # poly = extensions.IntertialParamPoly(au,bu,cu,du,av,bv,cv,dv,prange,length)

        pv.add_geometry(poly)
        length = pv.getTotalLength() 

        laneSections = self.laneBuilder.getStandardLanes(n_lanes, lane_offset, laneSides,
                                                            roadLength=length, 
                                                            isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
                                                            isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane)
        # create lanes
        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction, curveType=StandardCurveTypes.Poly)
        return road
