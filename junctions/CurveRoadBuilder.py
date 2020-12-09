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

    def __init__(self, country = CountryCodes.US):
        self.STD_ROADMARK = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)
        self.STD_START_CLOTH = 1/1000000000
        self.country = country
        self.laneBuilder = LaneBuilder()
        pass

    
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
            error = f"Unkown curveType {curveType}"
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
        
        pv = self.createPVForArcWithCloths(curvature, arcAngle, clothAngle)
        length = pv.getTotalLength()

        
        
        laneSections = self.laneBuilder.getStandardLanes(n_lanes, lane_offset, laneSides,
                                                            roadLength=length, 
                                                            isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
                                                            isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane)


        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction, curveType=StandardCurveTypes.LongArc)
        return road

    
    def createSimpleCurveWithLongArc(self, connectionRoadId, angleBetweenEndpoints, isJunction = False, curvature = StandardCurvature.Medium.value): 
        
        junction = extensions.getJunctionSelection(isJunction)

        totalRotation = np.pi - angleBetweenEndpoints

        # most of the angleBetweenEndpoints should be assigned to the Arc
        arcAngle = totalRotation * 0.9 # main curve
        clothAngle = (totalRotation * 0.1) / 2 # curve more.

        # print(f"arcAngle: {math.degrees(arcAngle)}")
        # print(f"clothAngle: {math.degrees(clothAngle)}")

        return pyodrx.create_cloth_arc_cloth(curvature, arc_angle=arcAngle, cloth_angle=clothAngle, r_id=connectionRoadId, junction = junction)

    
    def createS(self, connectionRoadId, angleBetweenEndpoints, isJunction = False, curvature = StandardCurvature.Medium.value): 
        """Here the angleBetweenEndpoints are used for the first road and S mid point, and S mid point and Second road

        Args:
            connectionRoadId ([type]): [description]
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
        r_id = connectionRoadId
        cloth_start = self.STD_START_CLOTH
        n_lanes = 1
        lane_offset = 3

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

        # create lanes
        road =  self.composeRoadWithStandardLanes(n_lanes, lane_offset, r_id, pv, junction)
        road.curveType = StandardCurveTypes.S
        return road
    