import numpy as np
import os
import pyodrx, extensions
import math

from junctions.StandardCurvatures import StandardCurvature
from junctions.StandardCurveTypes import StandardCurveTypes
from extensions.ExtendedRoad import ExtendedRoad


class RoadBuilder:

    def __init__(self):
        self.STD_ROADMARK = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)
        self.STD_START_CLOTH = 1/1000000000

    def getJunctionSelection(self, isJunction):
        if isJunction:
            return 1
        return -1

    def createRandomCurve(self, connectionRoadId, angleBetweenRoads, isJunction = False):
        
        """The magic curveRoad

        Args:
            angleBetweenRoads ([type]): The angle between the roads which this connectionRoad is suppose to connect together
            connectionRoadId ([type]): id to be assigned to the new connection road.
        """

        # 1. get random curvature
        curvature = StandardCurvature.getRandomValue()
        if curvature > StandardCurvature.MediumWide.value:
            curvature = StandardCurvature.MediumWide.value # clipping to medium wide

        # 2 random curve type
        randomCurveType = StandardCurveTypes.getRandomItem()

        road = self.createCurve(connectionRoadId, angleBetweenRoads, isJunction, curvature=curvature, curveType=randomCurveType)
        return road


    def createCurve(self, connectionRoadId, angleBetweenEndpoints, isJunction = False, curvature = StandardCurvature.Medium.value, curveType=StandardCurveTypes.Simple):

        if curveType is StandardCurveTypes.Simple:
            return self.createSimpleCurve(connectionRoadId, angleBetweenEndpoints, isJunction, curvature)
        elif curveType is StandardCurveTypes.LongArc:
            return self.createSimpleCurveWithLongArc(connectionRoadId, angleBetweenEndpoints, isJunction, curvature)
        elif curveType is StandardCurveTypes.S:
            return self.createS(connectionRoadId, angleBetweenEndpoints, isJunction, curvature)
        else:
            raise Exception(f"Unkown curveType {curveType}")



    def createSimpleCurve(self, connectionRoadId, angleBetweenEndpoints, isJunction = False, curvature = StandardCurvature.Medium.value):

        junction = self.getJunctionSelection(isJunction)
        totalRotation = np.pi - angleBetweenEndpoints
        arcAngle = np.pi / 10000000
        clothAngle = totalRotation / 2
        
        return pyodrx.create_cloth_arc_cloth(curvature, arc_angle=arcAngle, cloth_angle=clothAngle, r_id=connectionRoadId, junction = junction)

    
    def createSimpleCurveWithLongArc(self, connectionRoadId, angleBetweenEndpoints, isJunction = False, curvature = StandardCurvature.Medium.value): 
        
        junction = self.getJunctionSelection(isJunction)

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
        
        junction = self.getJunctionSelection(isJunction)

        totalRotation = np.pi - angleBetweenEndpoints

        # most of the angleBetweenEndpoints should be assigned to the Arc
        arcAngle = totalRotation
        clothAngle = (totalRotation * 0.1) / 2 # curve more.

        arc_curv = curvature 
        arc_angle = arcAngle 
        cloth_angle = clothAngle 
        r_id = connectionRoadId
        cloth_start = self.STD_START_CLOTH
        n_lanes = 1
        lane_offset = 3

        pv = pyodrx.PlanView()
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
        spiral1 = pyodrx.Spiral(cloth_start, arc_curv, angle=cloth_angle)
        arc = pyodrx.Arc(arc_curv, angle=arc_angle )
        arc2 = pyodrx.Arc(arc_curv2, angle = -arc_angle2)
        spiral2 = pyodrx.Spiral(-arc_curv, cloth_start, angle= -cloth_angle)

        pv.add_geometry(spiral1)
        pv.add_geometry(arc)
        pv.add_geometry(arc2)
        pv.add_geometry(spiral2)

        # create lanes
        lsec = pyodrx.LaneSection(0, pyodrx.standard_lane())
        for i in range(1, n_lanes+1, 1):
            lsec.add_right_lane(pyodrx.standard_lane(lane_offset))
            lsec.add_left_lane(pyodrx.standard_lane(lane_offset))
        laneSections = extensions.LaneSections()
        laneSections.add_lanesection(lsec)

        # create road
        road = ExtendedRoad(r_id, pv, laneSections, road_type=junction)
        road.curveType = StandardCurveTypes.S
        return road

