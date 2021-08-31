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
from junctions.Intersection import Intersection
import logging

class ThreeWayJunctionBuilder(SequentialJunctionBuilder):
    

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


    def ThreeWayJunctionWithAngle(self, 
                                  id, 
                                  angleBetweenRoads=np.pi/4, 
                                  firstRoadId=0,
                                  maxLanePerSide=2,
                                  minLanePerSide=0,
                                  internalConnections=True,
                                  cp1=pyodrx.ContactPoint.end,
                                  randomState=None,
                                  internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY,
                                  uTurnLanes=1,
                                  getAsOdr=True):

        if angleBetweenRoads < np.pi/9 or angleBetweenRoads > np.pi/2:
            raise Exception("Come up with a better angle")

        outsideRoads = []
        geoConnectionRoads = []        
        roads = []
        incidentContactPoints = []

        if randomState is not None:
            np.random.set_state(randomState)

        if cp1 == pyodrx.ContactPoint.end:
            firstRoad = self.createRandomStraightRoad(0, maxLanePerSide=maxLanePerSide, minLanePerSide=minLanePerSide, skipEndpoint=pyodrx.ContactPoint.start) # first road
        else:
            firstRoad = self.createRandomStraightRoad(0, maxLanePerSide=maxLanePerSide, minLanePerSide=minLanePerSide, skipEndpoint=pyodrx.ContactPoint.end) # first road

        firstRoad.id = firstRoadId
        roads.append(firstRoad)
        outsideRoads.append(firstRoad)
        incidentContactPoints.append(cp1)

        # second road

        secondConnectionRoadId = firstRoadId + 1
        secondRoadId = firstRoadId + 2
        otherContactPoints = pyodrx.ContactPoint.start


        secondRoad = self.createRandomStraightRoad(secondRoadId, maxLanePerSide=maxLanePerSide, minLanePerSide=minLanePerSide, skipEndpoint=pyodrx.ContactPoint.end)
        outsideRoads.append(secondRoad)
        incidentContactPoints.append(otherContactPoints)
        prevLanes, nextLanes = self.laneBuilder.getClockwiseAdjacentLanes(firstRoad=roads[0], firstCp=cp1, 
                                                                        secondRoad=secondRoad, secondCP=otherContactPoints)

        maxLaneWidth = self.getMaxLaneWidth(prevLanes, nextLanes)
        secondConnectionRoad = self.createConnectionRoadWithAngle(roadId=secondConnectionRoadId, 
                                                                angleBetweenRoads=angleBetweenRoads,
                                                                maxLaneWidth=maxLaneWidth)
        geoConnectionRoads.append(secondConnectionRoad)
        # firstRoad.addExtendedSuccessor(secondConnectionRoad, 0, pyodrx.ContactPoint.start)
        # secondConnectionRoad.addExtendedPredecessor(firstRoad, 0, cp1)
        RoadLinker.createExtendedPredSuc(predRoad=firstRoad,
                                        predCp=cp1,
                                        sucRoad=secondConnectionRoad,
                                        sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=secondConnectionRoad, 
                                        predCp=pyodrx.ContactPoint.end, 
                                        sucRoad=secondRoad, 
                                        sucCP=otherContactPoints)
        roads.append(secondConnectionRoad)
        roads.append(secondRoad)
        odrName = 'ThreeWay' + 'givenAngle' + str(id)
        odr = extensions.createOdrByPredecessor(odrName, roads, [])


        # third road
        thirdConnectionRoadId = firstRoadId + 3
        thirdRoadId = firstRoadId + 4


        thirdRoad = self.createRandomStraightRoad(thirdRoadId, maxLanePerSide=maxLanePerSide, minLanePerSide=minLanePerSide, skipEndpoint=pyodrx.ContactPoint.end)
        outsideRoads.append(thirdRoad)
        incidentContactPoints.append(otherContactPoints)

        roadLen = roads[1].length()
        thirdConnectionRoad = self.straightRoadBuilder.create(roadId=thirdConnectionRoadId, 
                                                            length=roadLen)
        geoConnectionRoads.append(thirdConnectionRoad)
        RoadLinker.createExtendedPredSuc(predRoad=firstRoad,
                                        predCp=cp1,
                                        sucRoad=thirdConnectionRoad,
                                        sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=thirdConnectionRoad, 
                                        predCp=pyodrx.ContactPoint.end, 
                                        sucRoad=thirdRoad, 
                                        sucCP=otherContactPoints)
        roads.append(thirdConnectionRoad)
        roads.append(thirdRoad)
        odr.add_road(thirdConnectionRoad)
        odr.add_road(thirdRoad)
        odr.resetAndReadjust(byPredecessor=True)

        # last connection
        lastConnectionRoadId = firstRoadId + 5
        connectionRoadSecondAndThird = self.createConnectionFor2Roads(nextRoadId=lastConnectionRoadId,
                                                                    road1=secondRoad,
                                                                    road2=thirdRoad,
                                                                    junction=None,
                                                                    cp1=pyodrx.ContactPoint.start,
                                                                    cp2=pyodrx.ContactPoint.start)
        roads.append(connectionRoadSecondAndThird)
        geoConnectionRoads.append(connectionRoadSecondAndThird)
        odr.add_road(connectionRoadSecondAndThird)
        self.fixNumOutgoingLanes(outsideRoads, cp1)

        if internalConnections:
            singleLaneConectionRoadId = firstRoadId + 6
            internalConnections = self.connectionBuilder.createSingleLaneConnectionRoads(singleLaneConectionRoadId, outsideRoads, cp1, internalLinkStrategy)
            roads += internalConnections
            odr.updateRoads(roads)

        odr.resetAndReadjust(byPredecessor=True)

        if getAsOdr:
            return odr

        intersection = Intersection(id, outsideRoads, incidentContactPoints, geoConnectionRoads, odr)
        return intersection


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




        