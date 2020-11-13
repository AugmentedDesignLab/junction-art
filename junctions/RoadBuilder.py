import numpy as np
import os
import pyodrx, extensions
import math

from junctions.StandardCurvatures import StandardCurvature
from junctions.StandardCurveTypes import StandardCurveTypes
from extensions.ExtendedRoad import ExtendedRoad
from extensions.ExtendedPlanview import ExtendedPlanview
from scipy.interpolate import CubicHermiteSpline


class RoadBuilder:

    def __init__(self):
        self.STD_ROADMARK = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)
        self.STD_START_CLOTH = 1/1000000000
        pass


    def cloneRoadWithGeoLanesAndType(self, road, newId):
        """These items are referenced from the original road
        planview, lanes
        These items are not referenced (needs to be rebuilt)
        name, rule, links, successors, predecessors, adjusted

        Args:
            road ([type]): [description]
            newId ([type]): [description]
        """
        newRoad = pyodrx.Road(newId, road.planview, road.lanes, road.road_type)
        return newRoad

    

    def getJunctionSelection(self, isJunction):
        if isJunction:
            return 1
        return -1

    def createRandomCurve(self, connectionRoadId, angleBetweenRoads, isJunction = False, minCurvature = StandardCurvature.UltraWide.value):
        
        """The magic curveRoad

        Args:
            angleBetweenRoads ([type]): The angle between the roads which this connectionRoad is suppose to connect together
            connectionRoadId ([type]): id to be assigned to the new connection road.
            isJunction (bool): 
            minCurvature (float): should not be less than .5 for junctions. the random curvature will be >= minCurvature.
        """

        # 1. get random curvature
        curvature = StandardCurvature.getRandomValue()
        if curvature < minCurvature:
            curvature = minCurvature # clipping to medium wide
        
        # 3. clip to a min value if it's a junction. Otherwise the length would be too long to have it contained in a junction area
        if isJunction and curvature < StandardCurvature.MediumSharp.value:
            curvature = StandardCurvature.MediumSharp.value

        # 4. change the curvature sign randomly for clockwise or anti-clockwise rotation.
        if np.random.choice(2) > 0 :
            curvature = -curvature

        # 5. add a random noise to the curvature.

        curvature = curvature + (np.random.choice(10) / 10) * curvature

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
            error = f"Unkown curveType {curveType}"
            raise Exception(error)



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
        lsec = pyodrx.LaneSection(0, pyodrx.standard_lane())
        for _ in range(1, n_lanes+1, 1):
            lsec.add_right_lane(pyodrx.standard_lane(lane_offset))
            lsec.add_left_lane(pyodrx.standard_lane(lane_offset))
        laneSections = extensions.LaneSections()
        laneSections.add_lanesection(lsec)

        # create road
        road = ExtendedRoad(r_id, pv, laneSections, road_type=junction)
        road.curveType = StandardCurveTypes.S
        return road
    

    def createCurveByLength(self, roadId, length, isJunction = False, curvature = StandardCurvature.Medium.value):

        junction = self.getJunctionSelection(isJunction)

        n_lanes = 1
        lane_offset = 3

        pv = ExtendedPlanview()
        arc = pyodrx.Arc(curvature, length=length )
        pv.add_geometry(arc)

        # create lanes
        lsec = pyodrx.LaneSection(0, pyodrx.standard_lane())
        for _ in range(1, n_lanes+1, 1):
            lsec.add_right_lane(pyodrx.standard_lane(lane_offset))
            lsec.add_left_lane(pyodrx.standard_lane(lane_offset))
        laneSections = extensions.LaneSections()
        laneSections.add_lanesection(lsec)

        # create road
        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction)
        road.curveType = StandardCurveTypes.S
        return road

    # def createCurveWithEndpoints(self, start, end):

    def createParamPoly3(self, roadId, isJunction=False, 
        au=0,bu=20,cu=20,du= 10,
        av=0,bv=2,cv=20,dv= 10,
        prange='normalized',length=None):

        junction = self.getJunctionSelection(isJunction)

        n_lanes = 1
        lane_offset = 3

        pv = ExtendedPlanview()
        
        poly = pyodrx.ParamPoly3(au,bu,cu,du,av,bv,cv,dv,prange,length)
        # poly = extensions.IntertialParamPoly(au,bu,cu,du,av,bv,cv,dv,prange,length)

        pv.add_geometry(poly)

        # create lanes
        lsec = pyodrx.LaneSection(0, pyodrx.standard_lane())
        for _ in range(1, n_lanes+1, 1):
            lsec.add_right_lane(pyodrx.standard_lane(lane_offset))
            lsec.add_left_lane(pyodrx.standard_lane(lane_offset))
        laneSections = extensions.LaneSections()
        laneSections.add_lanesection(lsec)

        # create road
        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction)
        road.curveType = StandardCurveTypes.S
        return road


    def getConnectionRoadBetween(self, newRoadId, road1, road2, cp1 = pyodrx.ContactPoint.end, cp2 = pyodrx.ContactPoint.start, isJunction = True):
        """ Works only after roads has been adjusted.
        For now we will create a straight road which connects the reference lines of the roads, starts at second road and ends that the first.

        Args:
            road1 ([type]): first road
            road2 ([type]): second road
            cp1 ([type], optional): [description]. Defaults to pyodrx.ContactPoint.end. end for the roads which have end points in a junction
            cp2 ([type], optional): [description]. Defaults to pyodrx.ContactPoint.start. start for the roads which have start points in a junction
        """
        x1, y1, h1 = road1.getPosition(cp1)
        x2, y2, h2 = road2.getPosition(cp2)

        tangentMagnitude = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

        # some magic of converting intertial points to local points. local 0, 0 is the start point of the second road.
        # here the local frame corresponds to the starting point of the new connection road. It's heading is on u axis

        localRotation = h2 + np.pi # rotation of local frame wrt inertial frame.

        u1, v1 = self.inertialToLocal((x2, y2), localRotation, (x1, y1))
        u2 = 0
        v2 = 0

        # Now we need tangents in local reference frame

        localStartTangent = extensions.headingToTangent(0, tangentMagnitude)
        localEndTangent = extensions.headingToTangent(h1 - localRotation, tangentMagnitude)

        # will this magic survive?

        X = [u2, u1]
        Y = [v2, v1]
        tangentX = [localStartTangent[0], localEndTangent[0]]
        tangentY = [localStartTangent[1], localEndTangent[1]]

        print("connecting road X, Y, tangentX, tangentY")
        print(X)
        print(Y)
        print(tangentX)
        print(tangentY)

        p = [0, 1]

        hermiteX = CubicHermiteSpline(p, X, tangentX)
        hermiteY = CubicHermiteSpline(p, Y, tangentY)

        xCoeffs = hermiteX.c.flatten()
        yCoeffs = hermiteY.c.flatten()

        # scipy coefficient and open drive coefficents have opposite order.
        newConnection = self.createParamPoly3(
                                                newRoadId, 
                                                isJunction=isJunction,
                                                au=xCoeffs[3],
                                                bu=xCoeffs[2],
                                                cu=xCoeffs[1],
                                                du=xCoeffs[0],
                                                av=yCoeffs[3],
                                                bv=yCoeffs[2],
                                                cv=yCoeffs[1],
                                                dv=yCoeffs[0]

                                            )

        return newConnection



    def inertialToLocal(self, localCenter, localRotation, intertialPoint):

        uBeforeRotation = intertialPoint[0] - localCenter[0]
        vBeforeRotation = intertialPoint[1] - localCenter[1]

        u = uBeforeRotation * math.cos(localRotation) + vBeforeRotation * math.sin(localRotation)
        v = -uBeforeRotation * math.sin(localRotation) + vBeforeRotation * math.cos(localRotation) 

        return u, v