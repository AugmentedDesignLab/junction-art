from operator import ipow
from os import close
from typing_extensions import Literal
from junctionart.roundabout.Generator import Generator
from junctionart.junctions.IncidentPoint import IncidentPoint  # have to to fix
from junctionart.junctions.JunctionBuilder import JunctionBuilder
from junctionart.extensions.ExtendedRoad import ExtendedRoad
from junctionart.junctions.CurveRoadBuilder import CurveRoadBuilder
from junctionart.junctions.StraightRoadBuilder import StraightRoadBuilder
from junctionart.extensions.CountryCodes import CountryCodes
from junctionart.junctions.ODRHelper import ODRHelper
from junctionart.junctions.ConnectionBuilder import ConnectionBuilder
from junctionart.junctions.RoadLinker import RoadLinker
import pyodrx
import junctionart.extensions as extensions
from junctionart.junctions.RoadBuilder import RoadBuilder
from typing import List, Dict
import random
import math
import numpy as np


class ClassicGenerator(Generator):
    def __init__(self, country=CountryCodes.US, laneWidth=3) -> None:
        super().__init__()
        self.curveBuilder = CurveRoadBuilder()
        self.junctionBuilder = JunctionBuilder()
        self.countryCode = country
        self.laneWidth = laneWidth
        self.straightRoadBuilder = StraightRoadBuilder()
        self.roadBuilder = RoadBuilder()
        self.connectionBuilder = ConnectionBuilder()

    def generateWithIncidentPointConfiguration(
        self,
        ipConfig: List[Dict],
        firstRoadId=0,
        maxLanePerSide=2,
        minLanePerSide=0,
        skipEndpoint=None,
        odrId=0,
    ):

        # 0 construct incident points

        incidentPoints = self.parseIncidentPoints(ipConfig)

        # 1. get a circle
        center, radius = self.getCircle(incidentPoints)
        self.center = center
        self.radius = radius
        print(center.x, center.y, radius)
        # 2. make the circular road with segments

        nLanes = 1
        circularRoads, circularRoadStartPoints = self.getCircularRoads(
            center, radius, firstRoadId, nLanes, nSegments=10
        )
        self.createSuccPreRelationBetweenCircularRoads(circularRoads)

        odrName = "TempCircularRoads" + str(odrId)
        odr = extensions.createOdrByPredecessor(
            odrName, circularRoads, [], countryCode=self.countryCode
        )

        circularRoadsJointId = firstRoadId + len(circularRoads)
        circularRoadsJoint = self.junctionBuilder.createConnectionFor2Roads(
            nextRoadId=circularRoadsJointId,
            road1=circularRoads[-1],
            road2=circularRoads[0],
            junction=None,
            cp1=pyodrx.ContactPoint.end,
            cp2=pyodrx.ContactPoint.start,
        )

        circularRoads.append(circularRoadsJoint)
        odr.updateRoads(circularRoads)
        odr.resetAndReadjust(byPredecessor=True)
        temp_odr = ODRHelper.transform(
            odr,
            startX=circularRoadStartPoints[0].x,
            startY=circularRoadStartPoints[0].y,
            heading=0,
        )

        firstStraightRoadId = circularRoadsJointId + 1
        # 3. create 3-way intersections
        # 3.1 make straightRoads from incidentPoints
        straightRoads = self.createStraightRoads(
            incidentPoints, 30, firstStraightRoadId, 1, 1, None
        )
        # 3.2 work out nearest circle segment from straightRoads/incidentPoints
        closestCircularRoadIdForIncidentPoints = self.getClosestCircularRoadIdForIncidentPoints(
            incidentPoints, circularRoadStartPoints
        )
        # 3.3 make parampolies between straightRoads with respective circle segment(start and end)
        leftLinks, rightLinks = self.getLaneConfigForConnectionRoads(
            closestCircularRoadIdForIncidentPoints, straightRoads, circularRoads
        )
        roadDic = self.getRoadDic(straightRoads, circularRoads)
        rightConnectionRoads = self.getConnectionRoads(
            firstStraightRoadId + len(straightRoads),
            roadDic,
            pyodrx.ContactPoint.end,
            pyodrx.ContactPoint.end,
            rightLinks,
        )

        # 3.4 join parampolies with staightRoad and circle segment
        roads = []
        roads.extend(circularRoads)
        roads.extend(rightConnectionRoads)
        roads.extend(straightRoads)

        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)

        leftConnectionRoads = self.getConnectionRoads(
            firstStraightRoadId + 2 * len(straightRoads),
            roadDic,
            pyodrx.ContactPoint.start,
            pyodrx.ContactPoint.start,
            leftLinks,
        )
        roads.extend(leftConnectionRoads)

        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)
        odr = ODRHelper.transform(
            odr=odr,
            startX=circularRoadStartPoints[0].x,
            startY=circularRoadStartPoints[0].y,
            heading=0,
        )

        return odr

        # intersections = self.createIntersections(incidentPoints, circularRoads)

        # 4. create the  roundabout object

        pass

    def createSuccPredRelationBetweenRoads(
        self,
        straightRoads,
        leftParamPolyConnectionRoads,
        rightParamPolyConnectionRoads,
        leftClosestCircularRoads,
        rightClosestCircularRoads,
    ):
        roads = []
        for i in range(0, len(straightRoads)):
            RoadLinker.createExtendedPredSuc(
                predRoad=leftClosestCircularRoads[i],
                predCp=pyodrx.ContactPoint.end,
                sucRoad=leftParamPolyConnectionRoads[i],
                sucCP=pyodrx.ContactPoint.end,
            )
            RoadLinker.createExtendedPredSuc(
                predRoad=leftParamPolyConnectionRoads[i],
                predCp=pyodrx.ContactPoint.start,
                sucRoad=straightRoads[i],
                sucCP=pyodrx.ContactPoint.end,
            )

            RoadLinker.createExtendedPredSuc(
                predRoad=rightClosestCircularRoads[i],
                predCp=pyodrx.ContactPoint.start,
                sucRoad=rightParamPolyConnectionRoads[i],
                sucCP=pyodrx.ContactPoint.end,
            )
            RoadLinker.createExtendedPredSuc(
                predRoad=rightParamPolyConnectionRoads[i],
                predCp=pyodrx.ContactPoint.start,
                sucRoad=straightRoads[i],
                sucCP=pyodrx.ContactPoint.end,
            )
            roads.append(leftParamPolyConnectionRoads[i])
            roads.append(rightParamPolyConnectionRoads[i])
            roads.append(straightRoads[i])

        return roads

    def getLaneConfigForConnectionRoads(
        self, closestCircularRoadIdForIncidentPoints, straightRoads, circularRoads
    ):
        leftLinks = []
        rightLinks = []

        nStraightRoads = len(straightRoads)
        for i in range(nStraightRoads):
            closestCiruclarRoadId = closestCircularRoadIdForIncidentPoints[i]
            straightRoad = straightRoads[i]
            leftCircularRoad = circularRoads[closestCiruclarRoadId - 1]
            rightCircularRoad = (
                circularRoads[0]
                if (closestCiruclarRoadId + 1 == len(circularRoads))
                else circularRoads[closestCiruclarRoadId + 1]
            )
            rightIncoming = str(leftCircularRoad.id) + ":" + str(-1)
            leftIncoming = str(straightRoad.id) + ":" + str(1)
            rightOutgoing = str(straightRoad.id) + ":" + str(-1)
            leftOutgoing = str(rightCircularRoad.id) + ":" + str(-1)
            leftLink = (leftIncoming, leftOutgoing)
            rightLink = (rightIncoming, rightOutgoing)

            leftLinks.append(leftLink)
            rightLinks.append(rightLink)

        return leftLinks, rightLinks

    def getRoadDic(self, straightRoads, circularRoads):
        roadDic = {road.id: road for road in straightRoads}
        for road in circularRoads:
            roadDic[road.id] = road
        return roadDic

    def getConnectionRoads(self, startRoadId, roadDic, cp1, cp2, laneConfig):
        connectionRoads = self.connectionBuilder.createRoadsForRoundaboutLinkConfig(
            startRoadId, roadDic, cp1, cp2, laneConfig
        )
        return connectionRoads

    def getClosestCircularRoadIdForIncidentPoints(
        self, incidentPoints, circularRoadStartPoints
    ):
        closestCircularRoadIdForIncidentPoints = []
        for incidentPoint in incidentPoints:
            incidentPointWithoutHeading = Point(incidentPoint.x, incidentPoint.y)
            bestPoint = circularRoadStartPoints[0]
            bestDistance = self.__distance(incidentPointWithoutHeading, bestPoint)
            for circularRoadStartPoint in circularRoadStartPoints:
                bestPoint = (
                    circularRoadStartPoint
                    if (
                        self.__distance(
                            incidentPointWithoutHeading, circularRoadStartPoint
                        )
                        < bestDistance
                    )
                    else bestPoint
                )
                bestDistance = self.__distance(incidentPointWithoutHeading, bestPoint)

            closestCircularRoadId = circularRoadStartPoints.index(bestPoint)
            closestCircularRoadIdForIncidentPoints.append(closestCircularRoadId)

        return closestCircularRoadIdForIncidentPoints

    def parseIncidentPoints(self, ipConfig: List[Dict]):
        return [IncidentPoint.parseIncidentPoint(point) for point in ipConfig]

    def createStraightRoads(
        self,
        incidentPoints: List[IncidentPoint],
        straightRoadLen,
        firstRoadID,
        maxLanePerSide,
        minLanePerSide,
        skipEndpoint,
    ):

        roadID = firstRoadID
        straightRoads = []
        for incidentPoint in incidentPoints:
            distance = self.__distance(incidentPoint, self.center)
            roadLength = (
                distance - self.radius - 30 if (distance > self.radius + 30) else 0
            )

            roadLength = (
                distance - self.radius * 1.2 if (distance > self.radius * 1.2) else 0
            )
            straightRoad = self.straightRoadBuilder.createRandom(
                roadId=roadID,
                length=roadLength,
                maxLanePerSide=maxLanePerSide,
                minLanePerSide=minLanePerSide,
                skipEndpoint=skipEndpoint,
            )
            odrName = "tempODR_StraightRoad" + str(roadID)
            odrStraightRoad = extensions.createOdrByPredecessor(
                odrName, [straightRoad], [], countryCode=self.countryCode
            )
            newStartX, newStartY, newHeading = (
                incidentPoint.x,
                incidentPoint.y,
                incidentPoint.heading,
            )
            odrAfterTransform = ODRHelper.transform(
                odrStraightRoad, newStartX, newStartY, newHeading
            )
            straightRoads.append(straightRoad)
            roadID += 1

        return straightRoads

    def createSuccPreRelationBetweenCircularRoads(self, circularRoads):
        nCircularRoads = len(circularRoads)
        for i in range(nCircularRoads - 1):
            RoadLinker.createExtendedPredSuc(
                predRoad=circularRoads[i],
                predCp=pyodrx.ContactPoint.end,
                sucRoad=circularRoads[i + 1],
                sucCP=pyodrx.ContactPoint.start,
            )

    def getCircularRoads(self, center, radius, firstRoadId, nLanes=2, nSegments=10):
        roadLength = 2 * np.pi * radius / nSegments
        curvature = 1 / radius

        circularRoads = []
        circularRoadStartPoints = []

        for i in range(nSegments):
            circularRoad = self.curveBuilder.createCurveByLength(
                roadId=firstRoadId + i,
                length=roadLength,
                curvature=curvature,
                n_lanes=nLanes,
            )
            odrName = "tempODR_circularRoad" + str(i + 1)

            newHeading = i * (360 / nSegments)
            newX = center.x + radius * math.sin(math.radians(newHeading))
            newY = center.y - radius * math.cos(math.radians(newHeading))

            circularRoadStartPoints.append(Point(newX, newY))
            circularRoads.append(circularRoad)

        return circularRoads, circularRoadStartPoints

    def getCircle(self, incidentPoints: List[IncidentPoint]):
        optimalCenter, radius = self.getOptimalCircle(incidentPoints)
        # quality, optimalCenter, radius = self.getRandomizedCircle(incidentPoints, optimalCenter, radius)
        # NOTE : circularRandomizer does not work
        return optimalCenter, radius * 0.4

    def createIntersections(
        self, incidentPoints: List[IncidentPoint], circularRoads: List[ExtendedRoad]
    ):
        return []

    def getOptimalCircle(self, incidentPoints):
        if len(incidentPoints) == 2:
            center = Point(
                (incidentPoints[0].x + incidentPoints[1].x) / 2,
                (incidentPoints[0].y + incidentPoints[1].y) / 2,
            )
            radius = self.__distance(incidentPoints[0], incidentPoints[1]) / 2
            return center, radius

        sum_x = (
            sum_y
        ) = sum_xx = sum_yy = sum_xy = sum_xxy = sum_xyy = sum_xxx = sum_yyy = 0.0
        A = B = C = D = E = 0.0
        x2 = y2 = xy = xDiff = yDiff = 0.0
        for incidentPoint in incidentPoints:
            sum_x += incidentPoint.x
            sum_y += incidentPoint.y
            x2 = incidentPoint.x * incidentPoint.x
            y2 = incidentPoint.y * incidentPoint.y
            xy = incidentPoint.x * incidentPoint.y
            sum_xx += x2
            sum_yy += y2
            sum_xy += xy
            sum_xxy += x2 * incidentPoint.y
            sum_xyy += y2 * incidentPoint.x
            sum_xxx += x2 * incidentPoint.x
            sum_yyy += y2 * incidentPoint.y

        n = len(incidentPoints)
        A = n * sum_xx - sum_x * sum_x
        B = n * sum_xy - sum_x * sum_y
        C = n * sum_yy - sum_y * sum_y
        D = 0.5 * (n * (sum_xyy + sum_xxx) - sum_x * sum_yy - sum_x * sum_xx)
        E = 0.5 * (n * (sum_xxy + sum_yyy) - sum_y * sum_xx - sum_y * sum_yy)

        F = A * C - B * B
        centerX = (D * C - B * E) / F
        centerY = (A * E - B * D) / F
        center = Point(centerX, centerY)

        radius = 10000000
        for i in range(n):
            xDiff = incidentPoints[i].x - centerX
            yDiff = incidentPoints[i].y - centerY
            radius = min(radius, (xDiff * xDiff + yDiff * yDiff) ** 0.5)

        return center, radius
        # returns optimal circle (x, y, r) for the given list of points.

    def getRandomizedCircle(
        self, incidentPoints: List[IncidentPoint], optimalCenter, radius
    ):
        a = random.uniform(0, 2)
        b = random.uniform(0, 2)
        newX = optimalCenter.x * a
        newY = optimalCenter.y * b
        newCenter = Point(newX, newY)

        radius = 1000000
        resultQuality = 0
        for i in range(len(incidentPoints)):
            resultQuality += math.sqrt(
                (incidentPoints[i].x - newX) ** 2 + (incidentPoints[i].y - newY) ** 2
            )
            xDiff = incidentPoints[i].x - newX
            yDiff = incidentPoints[i].y - newY
            radius = min(radius, (xDiff * xDiff + yDiff * yDiff) ** 0.5)

        # radius *= 0.9
        resultQuality -= len(incidentPoints) * (radius)
        resultQuality /= len(incidentPoints)
        return (resultQuality), newCenter, radius

    def __distance(self, p, q):
        return math.sqrt((p.x - q.x) ** 2 + (p.y - q.y) ** 2)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
