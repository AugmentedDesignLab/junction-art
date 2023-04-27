from curses.ascii import NL
from operator import ipow
from os import close
from turtle import right
from typing_extensions import Literal
from fontTools import configLogger
import matplotlib.pyplot as plt
from junctionart.extensions.moreHelpers import getConnectionRoads
from junctionart.junctions.Geometry import Geometry
from junctionart.junctions.JunctionDef import JunctionDef
from junctionart.junctions.LaneConfiguration import LaneConfiguration
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
from junctionart.junctions.LaneSides import LaneSides
from junctionart.extensions.ExtendedLane import ExtendedLane
from junctionart.roundabout.Roundabout import Roundabout
import pyodrx
import junctionart.extensions as extensions
from junctionart.junctions.RoadBuilder import RoadBuilder
from typing import List, Dict
import random
import math
import numpy as np


class TurboGenerator(Generator):
    def __init__(self, country=CountryCodes.US, laneWidth=3) -> None:
        super().__init__()
        self.curveBuilder = CurveRoadBuilder()
        self.junctionBuilder = JunctionBuilder()
        self.countryCode = country
        self.laneWidth = laneWidth
        self.straightRoadBuilder = StraightRoadBuilder()
        self.roadBuilder = RoadBuilder()
        self.connectionBuilder = ConnectionBuilder()
        self.junctions = []
        self.circularRoadLens = 0
        self.outgoingLanesMerge = True
    
    def generateWithRoadDefinitionTurbo(
        self,
        roadDefinition: List[Dict],
        firstRoadId=0,
        odrId=0,
        outgoingLanesMerge = True,
    ):

        # 0 construct incident points
        self.outgoingLanesMerge = outgoingLanesMerge
        incidentPoints = self.parseIncidentPoints(roadDefinition)

        # 1. get a circle
        center, radius = self.getCircle(incidentPoints)
        self.center = center
        self.radius = radius
        self.offsets = self.getOffset(incidentPoints)
        print(center.x, center.y, radius)

        # 1.5 find two compatible points
        self.compatiblePoints, self.compatiblePointsId = self.getCompatiblePoints(incidentPoints)

        # 1.9 find the angle needed to shift 
        angleShift = self.getAngleShift(self.compatiblePoints)

        # 2. make the circular road with segments

        self.circularRoadLens = self.__findCircularRoadLanes(roadDefinition)

        circularRoads, circularRoadStartPoints, circularRoadsWithoutConnectionRoads = self.getTurboCircularRoads(
            center, radius, firstRoadId, self.circularRoadLens, nSegments=3*int(radius)
        )

        fixedCircularRoadStartPoints = self.rotateCircularRoadStartPoints(circularRoadStartPoints, angleShift)
        for p in circularRoadStartPoints:
            print(p.x, " " , p.y)

        odrName = "TempCircularRoads" + str(odrId)
        odr = extensions.createOdrByPredecessor(
            odrName, circularRoads, [], countryCode=self.countryCode
        )
        extraodr = extensions.createOdrByPredecessor(
            odrName, circularRoads, [], countryCode=self.countryCode
        )

        # self.rotateCircularRoads(circularRoads, circularRoadStartPoints)
        odr.resetAndReadjust(byPredecessor=True)
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
        tempodr = ODRHelper.transform(
            odr,
            startX=(circularRoadStartPoints[0].x - self.center.x )* np.cos(angleShift) - (circularRoadStartPoints[0].y - self.center.y)* np.sin(angleShift) + self.center.x,
            startY= (circularRoadStartPoints[0].x - self.center.x) * np.sin(angleShift) + (circularRoadStartPoints[0].y - self.center.y) * np.cos(angleShift) + self.center.y,
            heading=angleShift,
        )

        
        
        print("Angle Shift is : ", np.degrees(angleShift))

        firstStraightRoadId = circularRoadsJointId + 1
        # 3. create 3-way intersections
        # 3.1 make straightRoads from incidentPoints
        straightRoads = self.createStraightRoadsFromRoadDefinition(
            incidentPoints, 30, firstStraightRoadId, roadDefinition
        )

         # 3.1.5 work out straight road end point
        straightRoadEndPoints = self.getStraightRoadEndPoints(straightRoads)

        # 3.2 work out nearest circle segment from straightRoads/incidentPoints
        closestCircularRoadIdForIncidentPoints = self.getClosestCircularRoadIdForIncidentPoints(
            straightRoadEndPoints, fixedCircularRoadStartPoints, circularRoadsWithoutConnectionRoads, self.compatiblePointsId
        )
        # 3.3 make parampolies between straightRoads with respective circle segment(start and end)
        # leftLinks, rightLinks = self.getLaneConfigForConnectionRoads(
        #     closestCircularRoadIdForIncidentPoints, straightRoads, circularRoads
        # )
        leftLinks, rightLinks = self.getLaneConfigForConnectionRoadsTurbo(
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

        # self.widenStraightRoadLanes(straightRoads)
        
        # # 3.4 join parampolies with staightRoad and circle segment
        roads = []
        roads.extend(circularRoads)
        roads.extend(rightConnectionRoads)
        roads.extend(straightRoads)

        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)
        
        leftConnectionRoads = self.getConnectionRoads(
            firstStraightRoadId + len(straightRoads) + len(rightConnectionRoads),
            roadDic,
            pyodrx.ContactPoint.start,
            pyodrx.ContactPoint.start,
            leftLinks,
        )
        
        roads.extend(leftConnectionRoads)

        # self.widenConnectionLanes(leftConnectionRoads, rightConnectionRoads, straightRoads)

        odr.updateRoads(roads)
        # self.createJunctions(rightConnectionRoads, leftConnectionRoads, circularRoads, closestCircularRoadIdForIncidentPoints)
        # for junction in self.junctions:
        #     for road in junction.connections:
        #         print(road.junctionId)
        odr.resetAndReadjust(byPredecessor=True)
        odr = ODRHelper.transform(
            odr=odr,
            startX= (circularRoadStartPoints[0].x - self.center.x)  * np.cos(angleShift) - (circularRoadStartPoints[0].y - self.center.y) * np.sin(angleShift) + self.center.x,
            startY= (circularRoadStartPoints[0].x - self.center.x)  * np.sin(angleShift) + (circularRoadStartPoints[0].y - self.center.y) * np.cos(angleShift) + self.center.y,
            heading=angleShift,
        )


        
        self.straightRoads = straightRoads
        self.circularRoads = circularRoads
        self.incomingConnectionRoads = rightConnectionRoads
        self.outgoingConnectionRoads = leftConnectionRoads
        self.odr = odr

        return odr

    def getRoundabout(self):
        return Roundabout(0, self.countryCode, self.laneWidth, self.center, self.radius, self.offsets
        , self.straightRoads, self.incomingConnectionRoads, self.outgoingConnectionRoads, self.circularRoadLens
        ,self.circularRoads, self.junctions)
        
    def widenStraightRoadLanes(self, straightRoads):
        for road in straightRoads:
            outgoingLanes = LaneConfiguration.getOutgoingLanesOnARoad(road, pyodrx.ContactPoint.end, CountryCodes.US)
            incomingLanes = LaneConfiguration.getIncomingLanesOnARoad(road, pyodrx.ContactPoint.end, CountryCodes.US)
            for lane in outgoingLanes:
                d, c, b, a = Geometry.cubic_equation_with_width(4, 3, road.length())
                lane.a = a
                lane.b = b
                lane.c = c
                lane.d = d

            for lane in incomingLanes:
                if lane != incomingLanes[-1]:
                    continue
                d, c, b, a = Geometry.cubic_equation_with_width(4, 3, road.length())
                lane.a = a
                lane.b = b
                lane.c = c
                lane.d = d
                

    def widenConnectionLanes(self, leftConnections, rightConnections, straightRoads):
        # find the outer connections
        # find the length
        # find the lande object
        # widen
        i = 0
        j = 0
        for k in range(len(straightRoads)):
            road = straightRoads[k]
            outgoingLanes = LaneConfiguration.getOutgoingLanesOnARoad(road, pyodrx.ContactPoint.end, CountryCodes.US)
            incomingLanes = LaneConfiguration.getIncomingLanesOnARoad(road, pyodrx.ContactPoint.end, CountryCodes.US)
            # -ve severely = ingoing secondlast fix
            # +ve severely = outgoing secondLast fix

            # if self.offsets[i] > 0.4:
            #     print("hehehe", i)
            #     connectionLane = leftConnections[len(outgoingLanes) - 2].getFirstLaneSection().rightlanes[0]
            #     d, c, b, a = Geometry.cubic_equation_with_three_width(4, 5, 3, leftConnections[len(outgoingLanes) - 2].length())
            #     connectionLane.a = a
            #     connectionLane.b = b
            #     connectionLane.c = c
            #     connectionLane.d = d

            # elif self.offsets[i] < -0.4:
            #     print("nonono", i)
            #     connectionLane = rightConnections[len(incomingLanes) - 2].getFirstLaneSection().rightlanes[0]
            #     d, c, b, a = Geometry.cubic_equation_with_three_width(3, 5, 10, rightConnections[len(incomingLanes) - 2].length())
            #     connectionLane.a = a
            #     connectionLane.b = b
            #     connectionLane.c = c
            #     connectionLane.d = d
                

            for lane in outgoingLanes:
                if len(outgoingLanes) < 2 or lane != outgoingLanes[-2] or self.offsets[k] > -0.2:
                    i = i + 1
                    continue
                connectionLane = leftConnections[i].getFirstLaneSection().rightlanes[0]
                d, c, b, a = Geometry.cubic_equation_with_width(3, 6, leftConnections[i].length())
                connectionLane.a = a
                connectionLane.b = b
                connectionLane.c = c
                connectionLane.d = d
                i = i + 1

            for lane in incomingLanes:
                if len(incomingLanes) < 2 or lane != incomingLanes[-2] or self.offsets[k] < 0.2:
                    j = j + 1
                    continue
                connectionLane = rightConnections[j].getFirstLaneSection().rightlanes[0]
                d, c, b, a = Geometry.cubic_equation_with_width(6, 3, rightConnections[j].length())
                connectionLane.a = a
                connectionLane.b = b
                connectionLane.c = c
                connectionLane.d = d
                j = j + 1
        

        pass

    def createJunctions(self, rightConnections, leftConnections, circularRoads, closestCircularRoadIdForIncidentPoints):
        nJunctions = len(closestCircularRoadIdForIncidentPoints)
        for i in range(nJunctions):
            connectionRoads = []
            junction = JunctionDef(i, f"junction{i}")
            connectionRoads.append(rightConnections[i])
            connectionRoads.append(leftConnections[i])
            id = closestCircularRoadIdForIncidentPoints[i]
            connectionRoads.append(circularRoads[id])
            junction.buildWithoutConnection(connectionRoads=connectionRoads)
            self.junctions.append(junction)

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
        spread = 7
        nStraightRoads = len(straightRoads)
        nCircularRoads = len(circularRoads)
        for i in range(nStraightRoads):
            leftOffset = int((1 + self.offsets[i]) / 2 * spread)
            rightOffset = spread - leftOffset
            
            # print(spread)
            # print(leftOffset, rightOffset)
            closestCiruclarRoadId = closestCircularRoadIdForIncidentPoints[i]
            straightRoad = straightRoads[i]
            leftCircularRoadId = (closestCiruclarRoadId - leftOffset + nCircularRoads + int(14*self.offsets[i])) % nCircularRoads
            rightCircularRoadId = (closestCiruclarRoadId + rightOffset + int(14*self.offsets[i])) % nCircularRoads
            leftCircularRoad = circularRoads[leftCircularRoadId]
            rightCircularRoad = circularRoads[rightCircularRoadId]
            # print(LaneConfiguration.getOutgoingLaneIdsOnARoad(straightRoad, pyodrx.ContactPoint.end, CountryCodes.US), "outcoming")
            # print(LaneConfiguration.getIncomingLaneIdsOnARoad(straightRoad, pyodrx.ContactPoint.end, CountryCodes.US), "incoming")
            
            leftCircularRoadForEdge = circularRoads[leftCircularRoadId - 1]
            rightCircularRoadForEdge = circularRoads[(rightCircularRoadId + 1 ) % len(circularRoads)]

            nLeftLanes = len(LaneConfiguration.getOutgoingLaneIdsOnARoad(straightRoad, pyodrx.ContactPoint.end, CountryCodes.US))
            nRightLanes = len(LaneConfiguration.getIncomingLaneIdsOnARoad(straightRoad, pyodrx.ContactPoint.end, CountryCodes.US))
            
            for j in range(nLeftLanes):
                leftIncoming = str(straightRoad.id) + ":" + str(j + 1)
                if j == nLeftLanes - 1:
                    leftOutgoing = str(rightCircularRoadForEdge.id) + ":" + str(-j - 1  - (self.circularRoadLens - nLeftLanes))
                else:
                    leftOutgoing = str(rightCircularRoad.id) + ":" + str(-j - 1  - (self.circularRoadLens - nLeftLanes))
                leftLink = (leftIncoming, leftOutgoing)
                leftLinks.append(leftLink)

            for j in range(nRightLanes):
                if j == nRightLanes - 1:
                    rightIncoming = str(leftCircularRoadForEdge.id) + ":" + str(-self.circularRoadLens if self.outgoingLanesMerge == True else -j - 1  - (self.circularRoadLens - nRightLanes))
                else:
                    rightIncoming = str(leftCircularRoad.id) + ":" + str(-self.circularRoadLens if self.outgoingLanesMerge == True else -j - 1  - (self.circularRoadLens - nRightLanes))
                rightOutgoing = str(straightRoad.id) + ":" + str(-nRightLanes + j)
                rightLink = (rightIncoming, rightOutgoing)
                # print(rightLink)
                rightLinks.append(rightLink)


        return leftLinks, rightLinks
    def getLaneConfigForConnectionRoadsTurbo(
        self, closestCircularRoadIdForIncidentPoints, straightRoads, circularRoads
    ):
        leftLinks = []
        rightLinks = []
        spread = 7
        nStraightRoads = len(straightRoads)
        nCircularRoads = len(circularRoads)
        for i in range(nStraightRoads):
            leftOffset = int((1 + self.offsets[i]) / 2 * spread)
            rightOffset = spread - leftOffset
  
            closestCiruclarRoadId = closestCircularRoadIdForIncidentPoints[i]
            straightRoad = straightRoads[i]
            if i == self.compatiblePointsId[0] or i == self.compatiblePointsId[1]:
                # leftCircularRoadId = closestCiruclarRoadId - 2
                # rightCircularRoadId = closestCiruclarRoadId + 2
                leftCircularRoadId = (closestCiruclarRoadId - leftOffset + nCircularRoads + int(14*self.offsets[i])) % nCircularRoads
                rightCircularRoadId = (closestCiruclarRoadId + rightOffset + int(14*self.offsets[i])) % nCircularRoads
            else:
                leftCircularRoadId = (closestCiruclarRoadId - leftOffset + nCircularRoads + int(14*self.offsets[i])) % nCircularRoads
                rightCircularRoadId = (closestCiruclarRoadId + rightOffset + int(14*self.offsets[i])) % nCircularRoads
            leftCircularRoad = circularRoads[leftCircularRoadId]
            rightCircularRoad = circularRoads[rightCircularRoadId]

            
            leftCircularRoadForEdge = circularRoads[leftCircularRoadId-1]
            rightCircularRoadForEdge = circularRoads[(rightCircularRoadId + 1) % len(circularRoads)]

            nLeftLanes = len(LaneConfiguration.getOutgoingLaneIdsOnARoad(straightRoad, pyodrx.ContactPoint.end, CountryCodes.US))
            nRightLanes = len(LaneConfiguration.getIncomingLaneIdsOnARoad(straightRoad, pyodrx.ContactPoint.end, CountryCodes.US))
            
            for j in range(nLeftLanes):
                leftIncoming = str(straightRoad.id) + ":" + str(j + 1)
                if j == nLeftLanes - 1:
                    leftOutgoing = str(rightCircularRoadForEdge.id) + ":" + str(-j - 1  - (self.circularRoadLens - nLeftLanes))
                else:
                    leftOutgoing = str(rightCircularRoad.id) + ":" + str(-j - 1  - (self.circularRoadLens - nLeftLanes))
                leftLink = (leftIncoming, leftOutgoing)
                leftLinks.append(leftLink)

            for j in range(nRightLanes):
                if j == nRightLanes - 1:
                    rightIncoming = str(leftCircularRoadForEdge.id) + ":" + str(-self.circularRoadLens if self.outgoingLanesMerge == True else -j - 1  - (self.circularRoadLens - nRightLanes))
                else:
                    rightIncoming = str(leftCircularRoad.id) + ":" + str(-self.circularRoadLens if self.outgoingLanesMerge == True else -j - 1  - (self.circularRoadLens - nRightLanes))
                rightOutgoing = str(straightRoad.id) + ":" + str(-nRightLanes + j)
                rightLink = (rightIncoming, rightOutgoing)
                # print(rightLink)
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
        self, incidentPoints, circularRoadStartPoints, circularRoadsWithoutConnectionRoads, compatiblePointsId
    ):
        closestCircularRoadIdForIncidentPoints = []
        startPoint = circularRoadStartPoints[0]
        oppositeSidePoint = circularRoadStartPoints[len(circularRoadStartPoints) // 2]
        # print("start Point :", startPoint.x, startPoint.y, "end point : ", oppositeSidePoint.x, oppositeSidePoint.y)
        # print(compatiblePoints[0].x, " " , compatiblePoints[0].y, "   ", compatiblePoints[1].x, " ", compatiblePoints[1].y)
        for id, incidentPoint in enumerate(incidentPoints):
            print(incidentPoint.x, " ", incidentPoint.y)
            if id == compatiblePointsId[0]:
                print("yes equal to 0")
                if self.__distance(incidentPoint, startPoint) < self.__distance(incidentPoint, oppositeSidePoint):
                    closestCircularRoadIdForIncidentPoints.append(0)
                else:
                    closestCircularRoadIdForIncidentPoints.append(len(circularRoadStartPoints) // 2)
                continue
            elif id == compatiblePointsId[1]:
                print("yes equal t o 1")
                if self.__distance(incidentPoint, startPoint) < self.__distance(incidentPoint, oppositeSidePoint):
                    closestCircularRoadIdForIncidentPoints.append(0)
                else:
                    closestCircularRoadIdForIncidentPoints.append(len(circularRoadStartPoints) // 2)
                continue
                    
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

    def getOffset(self, incidentPoints):
        offsets = []
        for incidentPoint in incidentPoints:
            heading = incidentPoint.heading
            if heading >= np.pi:
                heading -= 2*np.pi
            if heading < -np.pi:
                heading += 2*np.pi

            angleInRad = np.arctan2(self.center.y - incidentPoint.y, self.center.x - incidentPoint.x) - heading
            while angleInRad > np.pi:
                angleInRad -= 2*np.pi

            while angleInRad <= -np.pi:
                angleInRad += 2*np.pi
                
            offsets.append(angleInRad * 2 / np.pi)
        # print(offsets)
        return offsets

    def parseIncidentPoints(self, ipConfig: List[Dict]):
        return [IncidentPoint.parseIncidentPoint(point) for point in ipConfig]

    def getStraightRoadEndPoints(self, straightRoads):
        straightRoadEndPoints = []
        for straightRoad in straightRoads:
            # print(straightRoad.getPosition(pyodrx.ContactPoint.end))
            x, y, h = straightRoad.getPosition(pyodrx.ContactPoint.end)
            straightRoadEndPoint = IncidentPoint(x, y, h)
            straightRoadEndPoints.append(straightRoadEndPoint)

        return straightRoadEndPoints


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
        for i in range(len(incidentPoints)):
            incidentPoint = incidentPoints[i]
            distance = self.__distance(incidentPoint, self.center)

            roadLength = (
                np.abs(self.offsets[i] + 10)*(distance - self.radius * 1.2) if (distance > self.radius * 1.2) else 0
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
    
    def createStraightRoadsFromRoadDefinition(self, incidentPoints: List[IncidentPoint], straightRoadLen, firstRoadID, roadDefinition):
        roadID = firstRoadID
        straightRoads = []
        for i in range(len(roadDefinition)):
            road = roadDefinition[i]
            incidentPoint = incidentPoints[i]
            distance = self.__distance(incidentPoint, self.center)

            roadLength = (
                (1 - np.abs(self.offsets[i])) * (distance - self.radius * 1.5) if (distance > self.radius * 1.5 and np.abs(self.offsets[i]) < 1) else 0
            )
            if road["medianType"] != None:
                straightRoad = self.straightRoadBuilder.createWithMedianRestrictedLane(
                    roadId=roadID,
                    n_lanes_left=road["leftLane"],
                    n_lanes_right=road["rightLane"],
                    length= roadLength,
                    medianType=road["medianType"],
                    medianWidth=2,
                    skipEndpoint=road["skipEndpoint"],
                )
            else:
                straightRoad = self.straightRoadBuilder.create(
                    roadId=roadID,
                    n_lanes_right=road["rightLane"],
                    n_lanes_left=road["leftLane"],
                    length=roadLength,
                )

            straightRoad.junctionCP = pyodrx.ContactPoint.start
            straightRoad.junctionRelation = "predecessor"

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
        nCircularRoads = len(circularRoads ) - 1
        for i in range(nCircularRoads):
            RoadLinker.createExtendedPredSuc(
                predRoad=circularRoads[i],
                predCp=pyodrx.ContactPoint.end,
                sucRoad=circularRoads[i + 1],
                sucCP=pyodrx.ContactPoint.start,
            )

        


    def getRealisticCircularRoads(self, points, connections, firstRoadId, nLanes):
        Geometry.randomizePoints(points, connections, self.radius)
        # drop the center point from points
        circularRoads = []
        circularRoadStartPoints = []
        points = points[ : -1]
        # plt.plot(points[:, 0], points[:, 1], "ro-")
        print(points)
        headings = []
        for point in points:
            grad = math.atan2(self.center.y - point[1], self.center.x - point[0])
            grad -= np.pi / 2
            headings.append(grad)

        for ind, point in enumerate(points):

            circularRoad = self.getConnectionRoadBetween(firstRoadId + ind, points[ind - 1, 0], 
                points[ind - 1][1], headings[ind - 1], points[ind][0], points[ind][1], headings[ind], n_lanes=nLanes, cp1=pyodrx.ContactPoint.end, cp2=pyodrx.ContactPoint.start)
            circularRoads.append(circularRoad)
            circularRoadStartPoints.append(Point(point[0], point[1]))

        return circularRoads, circularRoadStartPoints   
        
    def getConnectionRoadBetween(self, newRoadId, x1, y1, h1, x2, y2, h2, 
        cp1 = pyodrx.ContactPoint.end, cp2 = pyodrx.ContactPoint.start, isJunction = True, 
        n_lanes=1, lane_offset=3, laneSides=LaneSides.RIGHT):
        """ Works only after roads has been adjusted.
        For now we will create a straight road which connects the reference lines of the roads, starts at second road and ends that the first.

        Args:
            road1 ([type]): first road
            road2 ([type]): second road
            cp1 ([type], optional): [description]. Defaults to pyodrx.ContactPoint.end. end for the roads which have end points in a junction
            cp2 ([type], optional): [description]. Defaults to pyodrx.ContactPoint.start. start for the roads which have start points in a junction
        """

        xCoeffs, yCoeffs = Geometry.getCoeffsForParamPoly(x1, y1, h1, x2, y2, h2, cp1, cp2)

        # scipy coefficient and open drive coefficents have opposite order.
        newConnection = self.curveBuilder.createParamPoly4(
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

    def getCircularConnections(self, circularRoadStartPoints):
        length = len(circularRoadStartPoints)
        circularRoadPoints = np.zeros((length + 1, 2))
        circularRoadPoints[-1] = [self.center.x, self.center.y]
        for ind, point in enumerate(circularRoadStartPoints):
            circularRoadPoints[ind] = [point.x, point.y]
        
        connections = np.array([])
        for i, _ in enumerate(circularRoadPoints):
            if i == circularRoadPoints.shape[0] - 1:
                break
            u = i
            v = (i + 1) if i < circularRoadPoints.shape[0] - 2 else 0
            connections = np.append(connections, (u, v, np.math.dist(circularRoadPoints[u], circularRoadPoints[v])))
    
        for i in range(circularRoadPoints.shape[0] - 1):
            u = i
            v = -1
            connections = np.append(connections, (u, v, np.math.dist(circularRoadPoints[u], circularRoadPoints[v])))
    
        connections = connections.reshape((-1, 3))
        return circularRoadPoints, connections

    def __rotateCircularRoad(self, roadno, circularRoad, angleOffset, nSegments, yOffset = 0):
        
        newHeading = roadno * (360 / nSegments) + angleOffset
        newX = self.center.x + self.radius * math.sin(math.radians(newHeading))
        newY = self.center.y + yOffset - self.radius * math.cos(math.radians(newHeading))
        tempOdrCircularRoad = extensions.createOdrByPredecessor(
            'Rotated Ciruclar Road', [circularRoad], [], countryCode=CountryCodes.US
        )
        print(newX, newY, newHeading)
        odrAfterTransform = ODRHelper.transform(
            tempOdrCircularRoad, newX, newY, newHeading
        )
    


    def getTurboCircularRoads(self, center, radius, firstRoadId, nLanes=2, nSegments=10, spiral = 2):
        roadLength = 2 * np.pi * radius / nSegments
        curvature = 1 / radius
        circularRoadsWithoutConnectingRoads = []
        circularRoads = []
        circularRoadStartPoints = []
        # half hoye gele ektu niche dewa lagbe
        rid = 0
        for spiralId in range(spiral):
            tempRoads = []
            for i in range(nSegments // spiral):
                circularRoad = self.curveBuilder.createCurveByLength(
                    roadId=firstRoadId + rid + 1 if spiralId != 0 and i == 0 else firstRoadId + rid,
                    length=roadLength,
                    laneSides=LaneSides.RIGHT,
                    curvature=curvature,
                    n_lanes=2 if i < nSegments//spiral - 1 else 1,
                )

                roadNo = (spiralId) * (nSegments // spiral) + i
                # self.__rotateCircularRoad(roadNo, circularRoad, -55, nSegments)

                rid += 0 if spiralId != 0 and i == 0 else 1    
                if spiralId != 0 and i == 0: 
                    # self.__rotateCircularRoad(roadNo, circularRoad, 0, nSegments, -3)
                    tempOdrCircularRoad = extensions.createOdrByPredecessor(
                        'Rotated Ciruclar Road', [circularRoad], [], countryCode=CountryCodes.US
                    )
                    odrAfterTransform = ODRHelper.transform(
                        tempOdrCircularRoad, 0, 2*self.radius - 3, np.pi
                    )
                    circularRoadsJoint = self.junctionBuilder.createConnectionFor2Roads(
                        nextRoadId=firstRoadId + rid,
                        road1=circularRoads[-1],
                        road2=circularRoad,
                        n_lanes= 1,
                        laneSides=LaneSides.RIGHT,
                        junction=None,
                        cp1=pyodrx.ContactPoint.end,
                        cp2=pyodrx.ContactPoint.start,
                    )
                    rid += 2
                    circularRoads.append(circularRoadsJoint)
                tempRoads.append(circularRoad)
            self.createSuccPreRelationBetweenCircularRoads(tempRoads)
            circularRoads.extend(tempRoads)
            circularRoadsWithoutConnectingRoads.extend(tempRoads)
            odr = extensions.createOdrByPredecessor(
                'TurboTest', circularRoads, [], countryCode=self.countryCode
            )
        for i in range(nSegments):
            newHeading = i * (360 / nSegments)
            newX = center.x + radius * math.sin(math.radians(newHeading))
            newY = center.y - radius * math.cos(math.radians(newHeading))
            circularRoadStartPoints.append(Point(newX, newY))
        return circularRoads, circularRoadStartPoints, circularRoadsWithoutConnectingRoads
    def rotateCircularRoadStartPoints(self, oldCircularRoadStartPoints, angleShift):
        circularRoadStartPoints = []
        for oldCircularRoadStartPoint in oldCircularRoadStartPoints:
            circularRoadStartPoint = self.__rotate(oldCircularRoadStartPoint, angleShift)
            circularRoadStartPoints.append(circularRoadStartPoint)

        print(len(circularRoadStartPoints))
        return circularRoadStartPoints

    def __rotate(self, point, angleShift):
        newX=(point.x - self.center.x )* np.cos(angleShift) - (point.y - self.center.y)* np.sin(angleShift) + self.center.x
        newY= (point.x - self.center.x) * np.sin(angleShift) + (point.y - self.center.y) * np.cos(angleShift) + self.center.y
        return Point(newX, newY)

    def getTurboCircularRoads2(self, center, radius, firstRoadId, nLanes=2, nSegments=10, spiral = 2):
        roadLength = 2 * np.pi * radius / nSegments
        curvature = 1 / radius
        circularRoads = []
        circularRoadStartPoints = []
        # half hoye gele ektu niche dewa lagbe
        rid = 0
        
        for i in range(nSegments):
            circularRoad = self.curveBuilder.createCurveByLength(
                roadId=firstRoadId + i,
                length=roadLength,
                laneSides=LaneSides.RIGHT,
                curvature=curvature,
                n_lanes=2 if i < nSegments//spiral - 1 else 1,
            )

            roadNo = i
            if i == nSegments / 2: 
                self.__rotateCircularRoad(roadNo, circularRoad, -55, nSegments, -3)
            else:
                self.__rotateCircularRoad(roadNo, circularRoad, -55, nSegments)

                
            circularRoads.append(circularRoad)

        self.createSuccPreRelationBetweenCircularRoads(circularRoads)
        odr = extensions.createOdrByPredecessor(
            'TurboTest', circularRoads, [], countryCode=self.countryCode
        )
        for i in range(nSegments):
            newHeading = i * (360 / nSegments)
            newX = center.x + radius * math.sin(math.radians(newHeading))
            newY = center.y - radius * math.cos(math.radians(newHeading))
            circularRoadStartPoints.append(Point(newX, newY))
        return circularRoads, circularRoadStartPoints
        

    def getCircle(self, incidentPoints: List[IncidentPoint]):
        optimalCenter, radius = self.getOptimalCircle(incidentPoints)
        # quality, optimalCenter, radius = self.getRandomizedCircle(incidentPoints, optimalCenter, radius)
        # NOTE : circularRandomizer does not work
        return optimalCenter, radius * 0.4

    def getAngleShift(self, compatiblePoints):
        # find the gradient between pointA and center (might be pointB too not sure)
        # returns angle in degree
        pointA, pointB = compatiblePoints
        print(self.compatiblePoints[0].x, " ", self.compatiblePoints[0].y)
        print(self.compatiblePoints[1].x, " ", self.compatiblePoints[1].y)

        dy = (pointA.y - self.center.y) 
        dx = (pointA.x - self.center.x)
        # gradient = dy / dx
        angleBetweenPointandCenter = np.arctan2(dy, dx) + np.pi / 2

        return (angleBetweenPointandCenter)

    def getCompatiblePoints(self, incidentPoints):
        # take the pair of points with the highest heading difference (180)
        # so that they are opposite
        # need a better idea involving their coordinates too
        bestDifference = 10000
        compatiblePoints = None
        compatiblePointsId = None
        for i in range(len(incidentPoints)):
            for j in range(len(incidentPoints)):
                pointA = incidentPoints[i] 
                pointB = incidentPoints[j]
                if pointA != pointB:
                    difference = np.absolute(np.pi - np.absolute(pointA.heading - pointB.heading))
                    angle1 = np.arctan2(pointA.y-self.center.y, pointA.y-self.center.x)
                    angle2 = np.arctan2(self.center.y-pointB.y, self.center.x-pointB.x)
                    difference2 = np.absolute(angle1-angle2)
                    # difference *= 180/np.pi
                    difference += difference2
                    if bestDifference > difference:
                        compatiblePoints = (pointA, pointB)
                        compatiblePointsId = (i, j)
                        bestDifference = difference

        return compatiblePoints, compatiblePointsId

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

    def __findCircularRoadLanes(self, roadDefinition):
        nLanes = 0
        for road in roadDefinition:
            if road["leftLane"] > nLanes:
                nLanes = road["leftLane"]
            elif road["rightLane"] > nLanes:
                nLanes = road["rightLane"]
        
        return nLanes

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
