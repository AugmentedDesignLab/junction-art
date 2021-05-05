import os, dill
import pyodrx, math
from junctions.RoadBuilder import RoadBuilder
import numpy as np
import extensions
from junctions.LaneSides import LaneSides
from junctions.Direction import CircularDirection
from junctions.JunctionAreaTypes import JunctionAreaTypes
from junctions.StraightRoadBuilder import StraightRoadBuilder
from extensions.ExtendedRoad import ExtendedRoad
from junctions.RoadLinker import RoadLinker
from junctions.JunctionBuilder import JunctionBuilder
from junctions.StandardCurveTypes import StandardCurveTypes
from junctions.AngleCurvatureMap import AngleCurvatureMap
from extensions.CountryCodes import CountryCodes
from junctions.LaneConfiguration import LaneConfigurationStrategies
from junctions.LaneConfiguration import LaneConfiguration
from junctions.SequentialJunctionBuilder import SequentialJunctionBuilder
import logging

class ThreeWayJunction(SequentialJunctionBuilder):
    

    def __init__(self, roadBuilder = None,
                straightRoadLen = 10,
                minAngle = np.pi/9, 
                maxAngle = np.pi/4, 
                country=CountryCodes.US, 
                random_seed=40,
                minConnectionLength=None,
                maxConnectionLength=None,
                probMinAngle=None,
                probLongConnection=None,
                probRestrictedLane=None):


        super().__init__(roadBuilder = roadBuilder,
                    straightRoadLen = straightRoadLen,
                    minAngle = minAngle, 
                    maxAngle = maxAngle, 
                    country=country, 
                    random_seed=random_seed,
                    minConnectionLength=minConnectionLength,
                    maxConnectionLength=maxConnectionLength,
                    probMinAngle=probMinAngle,
                    probLongConnection=probLongConnection,
                    probRestrictedLane=probRestrictedLane
                    )
        self.name = "ThreeWayJunctionBuilder"


    def ThreeWayJunctionWithAngle(self, odrId, 
                                    angleBetweenRoads=np.pi/4, 
                                    maxLanePerSide=2,
                                    minLanePerSide=0,
                                    internalConnections=True,
                                    cp1=pyodrx.ContactPoint.end,
                                    randomState=None,
                                    internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                                    uTurnLanes=1):

        if angleBetweenRoads < np.pi/9 or angleBetweenRoads > np.pi/2:
            raise Exception("Come up with a better angle")

        outsideRoad = []
        roads = []

        if cp1 == pyodrx.ContactPoint.end:
            firstRoad = self.createRandomStraightRoad(0, maxLanePerSide=maxLanePerSide, minLanePerSide=minLanePerSide, skipEndpoint=pyodrx.ContactPoint.start) # first road
        else:
            firstRoad = self.createRandomStraightRoad(0, maxLanePerSide=maxLanePerSide, minLanePerSide=minLanePerSide, skipEndpoint=pyodrx.ContactPoint.end) # first road

        roads.append(firstRoad)
        outsideRoad.append(firstRoad)

        # second road

        secondRoad = self.createRandomStraightRoad(2, maxLanePerSide=maxLanePerSide, minLanePerSide=minLanePerSide, skipEndpoint=pyodrx.ContactPoint.end)
        outsideRoad.append(secondRoad)
        prevLanes, nextLanes = self.laneBuilder.getClockwiseAdjacentLanes(firstRoad=roads[0], firstCp=cp1, 
                                                                        secondRoad=secondRoad, secondCP=pyodrx.ContactPoint.start)

        maxLaneWidth = self.getMaxLaneWidth(prevLanes, nextLanes)
        secondConnectionRoad = self.createConnectionRoadWithAngle(roadId=1, 
                                                                angleBetweenRoads=angleBetweenRoads,
                                                                maxLaneWidth=maxLaneWidth)
        # firstRoad.addExtendedSuccessor(secondConnectionRoad, 0, pyodrx.ContactPoint.start)
        # secondConnectionRoad.addExtendedPredecessor(firstRoad, 0, cp1)
        RoadLinker.createExtendedPredSuc(predRoad=firstRoad,
                                        predCp=cp1,
                                        sucRoad=secondConnectionRoad,
                                        sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=secondConnectionRoad, 
                                        predCp=pyodrx.ContactPoint.end, 
                                        sucRoad=secondRoad, 
                                        sucCP=pyodrx.ContactPoint.start)
        roads.append(secondConnectionRoad)
        roads.append(secondRoad)
        odrName = 'ThreeWay' + 'givenAngle' + str(odrId)
        odr = extensions.createOdrByPredecessor(odrName, roads, [])


        # third road
        thirdRoad = self.createRandomStraightRoad(4, maxLanePerSide=maxLanePerSide, minLanePerSide=minLanePerSide, skipEndpoint=pyodrx.ContactPoint.end)
        outsideRoad.append(thirdRoad)
        roadLen = roads[1].length()
        thirdConnectionRoad = self.straightRoadBuilder.create(roadId=3, 
                                                            length=roadLen)
        RoadLinker.createExtendedPredSuc(predRoad=firstRoad,
                                        predCp=cp1,
                                        sucRoad=thirdConnectionRoad,
                                        sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=thirdConnectionRoad, 
                                        predCp=pyodrx.ContactPoint.end, 
                                        sucRoad=thirdRoad, 
                                        sucCP=pyodrx.ContactPoint.start)
        roads.append(thirdConnectionRoad)
        roads.append(thirdRoad)
        odr.add_road(thirdConnectionRoad)
        odr.add_road(thirdRoad)
        odr.resetAndReadjust(byPredecessor=True)

        # last connection
        connectioRoadSecondAndThird = self.createConnectionFor2Roads(nextRoadId=5,
                                                                    road1=secondRoad,
                                                                    road2=thirdRoad,
                                                                    junction=None,
                                                                    cp1=pyodrx.ContactPoint.start,
                                                                    cp2=pyodrx.ContactPoint.start)
        roads.append(connectioRoadSecondAndThird)
        odr.add_road(connectioRoadSecondAndThird)
        self.fixNumOutgoingLanes(outsideRoad, cp1)

        if internalConnections:
            internalConnections = self.connectionBuilder.createSingleLaneConnectionRoads(6, outsideRoad, cp1, internalLinkStrategy)
            roads += internalConnections
            odr.updateRoads(roads)

        odr.resetAndReadjust(byPredecessor=True)
        return odr


    def getMaxLaneWidth(self, prevLanes, nextLanes):
        maxLaneWidth = max(len(prevLanes), len(nextLanes)) * self.laneWidth
        if len(prevLanes) == 0 or len(nextLanes) == 0:
            maxLaneWidth = ((len(prevLanes) + len(nextLanes)) * self.laneWidth) / 2
        return maxLaneWidth



    def createConnectionRoadWithAngle(self, roadId, angleBetweenRoads, maxLaneWidth):

        curvature = AngleCurvatureMap.getMaxCurvatureAgainstMaxRoadWidth(angleBetweenRoads, maxLaneWidth=maxLaneWidth)
        newConnection = self.curveBuilder.create(roadId=roadId, 
                                                angleBetweenEndpoints=angleBetweenRoads,
                                                isJunction=True, curvature=curvature, 
                                                curveType=StandardCurveTypes.LongArc)
        return newConnection




        