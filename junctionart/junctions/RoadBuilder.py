import numpy as np
import os
import pyodrx, extensions
import math

from junctionart.junctions.LaneSides import LaneSides
from junctionart.junctions.StandardCurvatures import StandardCurvature
from junctionart.junctions.StandardCurveTypes import StandardCurveTypes
from junctionart.extensions.ExtendedRoad import ExtendedRoad
from junctionart.extensions.ExtendedPlanview import ExtendedPlanview
from scipy.interpolate import CubicHermiteSpline

from junctionart.junctions.RoadSeries import RoadSeries
from junctionart.junctions.Direction import CircularDirection
from junctionart.junctions.Geometry import Geometry
from junctionart.junctions.LaneBuilder import LaneBuilder
from junctionart.junctions.RoadLinker import RoadLinker
from junctionart.junctions.CurveRoadBuilder import CurveRoadBuilder
from junctionart.extensions.CountryCodes import CountryCodes


class RoadBuilder:

    def __init__(self, country=CountryCodes.US):
        self.STD_ROADMARK = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)
        self.STD_START_CLOTH = 1/1000000000
        self.laneBuilder = LaneBuilder()
        self.curveBuilder = CurveRoadBuilder(country=country)
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
        randomCurveType = StandardCurveTypes.getRandomItemForCurve()

        road = self.curveBuilder.create(connectionRoadId, angleBetweenRoads, isJunction, curvature=curvature, curveType=randomCurveType)
        return road


    # def createCurve(self, connectionRoadId, angleBetweenEndpoints, isJunction = False, curvature = StandardCurvature.Medium.value, curveType=StandardCurveTypes.Simple):

    #     if curveType is StandardCurveTypes.Simple:
    #         return self.createSimpleCurve(connectionRoadId, angleBetweenEndpoints, isJunction, curvature)
    #     elif curveType is StandardCurveTypes.LongArc:
    #         return self.createSimpleCurveWithLongArc(connectionRoadId, angleBetweenEndpoints, isJunction, curvature)
    #     elif curveType is StandardCurveTypes.S:
    #         return self.createS(connectionRoadId, angleBetweenEndpoints, isJunction, curvature)
    #     else:
    #         error = f"Unkown curveType {curveType}"
    #         raise Exception(error)



    # def createSimpleCurve(self, connectionRoadId, angleBetweenEndpoints, isJunction = False, curvature = StandardCurvature.Medium.value):

    #     junction = self.getJunctionSelection(isJunction)
    #     totalRotation = np.pi - angleBetweenEndpoints
    #     arcAngle = np.pi / 10000000
    #     clothAngle = totalRotation / 2
        
    #     return pyodrx.create_cloth_arc_cloth(curvature, arc_angle=arcAngle, cloth_angle=clothAngle, r_id=connectionRoadId, junction = junction)

    
    # def createSimpleCurveWithLongArc(self, connectionRoadId, angleBetweenEndpoints, isJunction = False, curvature = StandardCurvature.Medium.value): 
        
    #     junction = self.getJunctionSelection(isJunction)

    #     totalRotation = np.pi - angleBetweenEndpoints

    #     # most of the angleBetweenEndpoints should be assigned to the Arc
    #     arcAngle = totalRotation * 0.9 # main curve
    #     clothAngle = (totalRotation * 0.1) / 2 # curve more.

    #     # print(f"arcAngle: {math.degrees(arcAngle)}")
    #     # print(f"clothAngle: {math.degrees(clothAngle)}")

    #     return pyodrx.create_cloth_arc_cloth(curvature, arc_angle=arcAngle, cloth_angle=clothAngle, r_id=connectionRoadId, junction = junction)


    def createSimpleCurveWithLongArcWithLaneNumberandOffset(self, connectionRoadId, angleBetweenEndpoints, isJunction = False, curvature = StandardCurvature.Medium.value, _lane_offset = 3, _n_lanes = 1): 
        
        junction = self.getJunctionSelection(isJunction)

        totalRotation = np.pi - angleBetweenEndpoints

        # most of the angleBetweenEndpoints should be assigned to the Arc
        arcAngle = totalRotation * 0.9 # main curve
        clothAngle = (totalRotation * 0.1) / 2 # curve more.

        # print(f"arcAngle: {math.degrees(arcAngle)}")
        # print(f"clothAngle: {math.degrees(clothAngle)}")

        return pyodrx.create_cloth_arc_cloth(curvature, arc_angle=arcAngle, cloth_angle=clothAngle, r_id=connectionRoadId, junction = junction,n_lanes = _n_lanes, lane_offset=_lane_offset)
    
    # def createS(self, connectionRoadId, angleBetweenEndpoints, isJunction = False, curvature = StandardCurvature.Medium.value): 
    #     """Here the angleBetweenEndpoints are used for the first road and S mid point, and S mid point and Second road

    #     Args:
    #         connectionRoadId ([type]): [description]
    #         angleBetweenEndpoints ([type]): used for the first road and S mid point, and S mid point and Second road. Use negative angles for interesting Ss
    #         isJunction (bool, optional): [description]. Defaults to False.
    #         curvature ([type], optional): [description]. Defaults to StandardCurvature.Medium.value.

    #     Returns:
    #         [type]: [description]
    #     """
        
    #     junction = self.getJunctionSelection(isJunction)

    #     totalRotation = np.pi - angleBetweenEndpoints

    #     # most of the angleBetweenEndpoints should be assigned to the Arc
    #     arcAngle = totalRotation * 0.9
    #     clothAngle = (totalRotation * 0.1) / 2 # curve more.

    #     arc_curv = curvature 
    #     arc_angle = arcAngle 
    #     cloth_angle = clothAngle 
    #     r_id = connectionRoadId
    #     cloth_start = self.STD_START_CLOTH
    #     n_lanes = 1
    #     lane_offset = 3

    #     pv = ExtendedPlanview()
    #     # adjust sign if angle is negative
    #     if cloth_angle < 0 and  arc_curv > 0:

    #         cloth_angle = -cloth_angle
    #         arc_curv = -arc_curv
    #         cloth_start = -cloth_start
    #         arc_angle = -arc_angle 

    #     # we are changing the second half of the S to have different arc angle and curvature.
    #     multiplier = np.random.choice(9) / 10
    #     arc_angle2 = arc_angle - arc_angle * multiplier
    #     arc_curv2 = -(arc_curv + arc_curv * multiplier) # the angle needs to be opposite for the second half.
        
    #     # create geometries
    #     spiral1 = extensions.ExtendedSpiral(cloth_start, arc_curv, angle=cloth_angle)
    #     arc = pyodrx.Arc(arc_curv, angle=arc_angle )
    #     arc2 = pyodrx.Arc(arc_curv2, angle = -arc_angle2)
    #     spiral2 = extensions.ExtendedSpiral(-arc_curv, cloth_start, angle= -cloth_angle)

    #     pv.add_geometry(spiral1)
    #     pv.add_geometry(arc)
    #     pv.add_geometry(arc2)
    #     pv.add_geometry(spiral2)

    #     # create lanes
    #     road =  self.composeRoadWithStandardLanes(n_lanes, lane_offset, r_id, pv, junction)
    #     road.curveType = StandardCurveTypes.S
    #     return road
    

    # def createCurveByLength(self, roadId, length, isJunction = False, curvature = StandardCurvature.Medium.value):

    #     junction = self.getJunctionSelection(isJunction)

    #     n_lanes = 1
    #     lane_offset = 3

    #     pv = ExtendedPlanview()
    #     arc = pyodrx.Arc(curvature, length=length )
    #     pv.add_geometry(arc)

    #     # create lanes
    #     road = self.composeRoadWithStandardLanes(n_lanes, lane_offset, roadId, pv, junction)
    #     road.curveType = StandardCurveTypes.LongArc
    #     return road

    # def createCurveWithEndpoints(self, start, end):

    # def createParamPoly3(self, roadId, isJunction=False, 
    #     au=0,bu=20,cu=20,du= 10,
    #     av=0,bv=2,cv=20,dv= 10,
    #     prange='normalized',
    #     length=None,
    #     n_lanes=1,
    #     lane_offset=3,
    #     laneSides=LaneSides.BOTH):

    #     junction = self.getJunctionSelection(isJunction)

    #     n_lanes = 1
    #     lane_offset = 3

    #     pv = ExtendedPlanview()
        
    #     poly = pyodrx.ParamPoly3(au,bu,cu,du,av,bv,cv,dv,prange,length)
    #     # poly = extensions.IntertialParamPoly(au,bu,cu,du,av,bv,cv,dv,prange,length)

    #     pv.add_geometry(poly)

    #     # create lanes
    #     road = self.composeRoadWithStandardLanes(n_lanes, lane_offset, roadId, pv, junction, laneSides=laneSides)
    #     road.curveType = StandardCurveTypes.Poly
    #     return road



    def composeRoadWithStandardLanes(self, n_lanes, lane_offset, roadId, pv, junction, laneSides=LaneSides.BOTH):
        """[summary]

        Args:
            n_lanes ([type]): [description]
            lane_offset ([type]): width
            roadId ([type]): [description]
            pv ([type]): [description]
            junction ([type]): [description]
            laneSides ([type], optional): where to put lanes wrt center lane. Defaults to LaneSides.BOTH.

        Returns:
            [type]: [description]
        """

        laneSections = self.laneBuilder.getStandardLanes(n_lanes, lane_offset, laneSides)
        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction)
        return road

    
    def createStraightRoad(self, roadId, length=100,junction = -1, n_lanes=1, lane_offset=3, 
                                    laneSides=LaneSides.BOTH):

        # create geometry
        line1 = pyodrx.Line(length)

        # create planviews
        planview1 = extensions.ExtendedPlanview()
        planview1.add_geometry(line1)

        road = self.composeRoadWithStandardLanes(n_lanes, lane_offset, roadId, planview1, junction, laneSides=laneSides)
        road.curveType = StandardCurveTypes.Line
        return road


    def getRelativeHeading(self, rootHeading, anotherHeading):
        return (anotherHeading + (np.pi * 2) - rootHeading) % (np.pi * 2)


    def getStraightRoadBetween(self, newRoadId, road1, road2, cp1 = pyodrx.ContactPoint.end, cp2 = pyodrx.ContactPoint.start, isJunction = True,
                                    n_lanes=1,
                                    lane_offset=3,
                                    laneSides=LaneSides.BOTH):
        
        junction = self.getJunctionSelection(isJunction)
        x1, y1, h1 = road1.getPosition(cp1)
        x2, y2, h2 = road2.getPosition(cp2)
        length = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        road = self.createStraightRoad(newRoadId, length=length, junction=junction, n_lanes=n_lanes, lane_offset=lane_offset, laneSides = laneSides)
        
        if cp1 == pyodrx.ContactPoint.start:
            h1 = h1 + np.pi
        
        if cp2 == pyodrx.ContactPoint.end:
            h2 = h2 + np.pi

        road.startHeading = self.getRelativeHeading(h1, h2)

        return road
    


    def getConnectionRoadBetween(self, newRoadId, road1, road2, cp1 = pyodrx.ContactPoint.end, cp2 = pyodrx.ContactPoint.start, isJunction = True,
                                    n_lanes=1,
                                    lane_offset=3,
                                    laneSides=LaneSides.BOTH):
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

        xCoeffs, yCoeffs = Geometry.getCoeffsForParamPoly(x1, y1, h1, x2, y2, h2, cp1, cp2)

        # scipy coefficient and open drive coefficents have opposite order.
        newConnection = self.curveBuilder.createParamPoly3(
                                                newRoadId, 
                                                isJunction=isJunction,
                                                au=xCoeffs[3],
                                                bu=xCoeffs[2],
                                                cu=xCoeffs[1],
                                                du=xCoeffs[0],
                                                av=yCoeffs[3],
                                                bv=yCoeffs[2],
                                                cv=yCoeffs[1],
                                                dv=yCoeffs[0],
                                                n_lanes=n_lanes,
                                                lane_offset=lane_offset,
                                                laneSides=laneSides

                                            )

        return newConnection



    def inertialToLocal(self, localCenter, localRotation, intertialPoint):

        uBeforeRotation = intertialPoint[0] - localCenter[0]
        vBeforeRotation = intertialPoint[1] - localCenter[1]

        u = uBeforeRotation * math.cos(localRotation) + vBeforeRotation * math.sin(localRotation)
        v = -uBeforeRotation * math.sin(localRotation) + vBeforeRotation * math.cos(localRotation) 

        return u, v


    def createRoundAboutConnection(self, connectionId, angleBetweenRoads, radius, n_lanes=1, 
                                laneSides=LaneSides.RIGHT, direction=CircularDirection.COUNTERCLOCK_WISE):
        
        roadStart, roadMain, roadEnd = self.createMShapeAndGetEachPartAsSeperateRoads(connectionId, 1, angleBetweenRoads, radius, n_lanes=n_lanes, 
                                                                                    laneSides=laneSides, direction=direction)

        return RoadSeries([roadStart, roadMain, roadEnd])
        

    def createMShape(self, roadId, junction, angleBetweenRoads, radius, n_lanes=1, laneSides = LaneSides.BOTH, direction=CircularDirection.CLOCK_WISE):
        """[summary]

        Args:
            roadId ([type]): [description]
            junction ([type]): -1 for road, 1 for connection
            angleBetweenRoads ([type]): [description]
            radius ([type]): [description]

        Returns:
            [type]: [description]
        """
        # angleBetweenRoads = np.pi - angleBetweenRoads

        # print(f"angleBetweenRoads {math.degrees(angleBetweenRoads)}")
        
        spiral1, curve1, mainCurve, curve3, spiral2 = self.getMGeometries(radius, angleBetweenRoads, direction)

        pv = extensions.ExtendedPlanview()
        pv.add_geometry(spiral1)
        pv.add_geometry(curve1)
        pv.add_geometry(mainCurve)
        pv.add_geometry(curve3)
        pv.add_geometry(spiral2)

        
        lane_offset = 3

        # create lanes
        return self.composeRoadWithStandardLanes(n_lanes, lane_offset, roadId, pv, junction, laneSides=laneSides)

    
    
    def createMShapeAndGetEachPartAsSeperateRoads(self, startRoadId, junction, angleBetweenRoads, radius, 
                                                n_lanes=1, lane_offset = 3, laneSides = LaneSides.BOTH, direction=CircularDirection.CLOCK_WISE):
        """5 components of an M shape as seperate roads.

        Args:
            startRoadId ([type]): RoadId of the first part. increments for each part.
            junction ([type]): -1 for road, 1 for connection
            angleBetweenRoads ([type]): [description]
            radius ([type]): [description]

        Returns:
            [type]: parts with successor and predecessors linked.
        """
        # angleBetweenRoads = np.pi - angleBetweenRoads

        # print(f"angleBetweenRoads {math.degrees(angleBetweenRoads)}")
        
        spiral1, curve1, mainCurve, curve3, spiral2 = self.getMGeometries(radius, angleBetweenRoads, direction=direction)

        pvStart = extensions.ExtendedPlanview()
        pvMain = extensions.ExtendedPlanview()
        pvEnd = extensions.ExtendedPlanview()

        pvStart.add_geometry(spiral1)
        pvStart.add_geometry(curve1)
        pvMain.add_geometry(mainCurve)
        pvEnd.add_geometry(curve3)
        pvEnd.add_geometry(spiral2)

        
        
        mainRoadId = startRoadId + 1
        endRoadId = mainRoadId + 1 
        # create lanes
        roadStart =  self.composeRoadWithStandardLanes(n_lanes, lane_offset, startRoadId, pvStart, junction, laneSides=laneSides)
        roadMain =  self.composeRoadWithStandardLanes(n_lanes, lane_offset, mainRoadId, pvMain, junction, laneSides=laneSides)
        roadEnd =  self.composeRoadWithStandardLanes(n_lanes, lane_offset, endRoadId, pvEnd, junction, laneSides=laneSides)

        RoadLinker.createExtendedPredSuc(predRoad=roadStart, predCp=pyodrx.ContactPoint.end, sucRoad=roadMain, sucCP= pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=roadMain, predCp=pyodrx.ContactPoint.end, sucRoad=roadEnd, sucCP= pyodrx.ContactPoint.start)


        return roadStart, roadMain, roadEnd



    def getMGeometries(self, radius, angleBetweenRoads, direction=CircularDirection.CLOCK_WISE):
        mainCurvature = -(1 / radius)
        miniCurvature = 1 / (radius / 4)

        spiralAngle = np.pi/20
        miniCurveAngle = np.pi/2 - spiralAngle


        if direction == CircularDirection.COUNTERCLOCK_WISE:
            miniCurvature = -miniCurvature
            mainCurvature = -mainCurvature



        # create

        spiral1 = pyodrx.Spiral(0.001, miniCurvature, angle=spiralAngle)
        curve1 = pyodrx.Arc(miniCurvature, angle=miniCurveAngle)
        mainCurve = pyodrx.Arc(mainCurvature, angle=angleBetweenRoads)
        curve3 = pyodrx.Arc(miniCurvature, angle=miniCurveAngle)
        spiral2 = pyodrx.Spiral(0.001, miniCurvature, angle=spiralAngle)
        return spiral1, curve1, mainCurve, curve3, spiral2

    