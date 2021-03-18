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
import logging


class SequentialJunctionBuilder(JunctionBuilder):

    def __init__(self, roadBuilder = None,
                straightRoadLen = 10,
                minAngle = np.pi/6, 
                maxAngle = 1.8 * np.pi, 
                country=CountryCodes.US, 
                random_seed=39
                ):
            
        super().__init__(roadBuilder=roadBuilder,
                        straightRoadLen=straightRoadLen,
                        minAngle=minAngle,
                        maxAngle=maxAngle,
                        country=country,
                        random_seed=random_seed
                        )
        self.name = 'SequentialJunctionBuilder'
    

    def drawLikeAPainter2L(self, odrId, maxNumberOfRoadsPerJunction, save=True, internalConnections=True, cp1=pyodrx.ContactPoint.end):
        if maxNumberOfRoadsPerJunction < 3:
            raise Exception("drawLikeAPainter is not for the weak. Please add more than 3 roads")

        
        maxLaneWidth = self.laneWidth 

        roads = []
        roads.append(self.straightRoadBuilder.create(0, length=self.straightRoadLen * 4)) # first road

        availableAngle = 1.8 * np.pi # 360 degrees
        maxAnglePerConnection = availableAngle / (maxNumberOfRoadsPerJunction - 1)
        action = self.actionAfterDrawingOne(roads, availableAngle, maxNumberOfRoadsPerJunction)
        nextRoadId = 1
        while (action != "end"):

            logging.debug(f"{self.name}: availableAngle {math.degrees(availableAngle)}, number of roads: {len(roads) / 2}")
            previousRoadId = nextRoadId - 1
            newConnectionId = nextRoadId
            nextRoadId += 1
            newRoadId = nextRoadId
            nextRoadId += 1

            # 1. create a road
            newRoad = self.straightRoadBuilder.create(newRoadId, length=self.straightRoadLen)

            # 2. create a new connection road
            newConnection, availableAngle = self.createGeoConnectionRoad(action, newConnectionId, availableAngle, maxAnglePerConnection, maxLaneWidth=maxLaneWidth)
            
            # 5 add new roads and increase road id
            roads.append(newConnection)
            roads.append(newRoad)

            # roads[previousRoadId].add_successor(pyodrx.ElementType.junction, newConnection.id)
            roads[previousRoadId].addExtendedSuccessor(newConnection, 0, pyodrx.ContactPoint.start)

            if newConnection.id == 1:
                # TODO this is a hack. It will not eventually work because outgoing roads' ends will come to join other junctions.
                newConnection.addExtendedPredecessor(roads[previousRoadId], 0 , cp1)
            else:
                newConnection.addExtendedPredecessor(roads[previousRoadId], 0 , pyodrx.ContactPoint.start)
            
            RoadLinker.createExtendedPredSuc(predRoad=newConnection, predCp=pyodrx.ContactPoint.end, sucRoad=newRoad, sucCP=pyodrx.ContactPoint.start)


            # 6 get next action
            action = self.actionAfterDrawingOne(roads, availableAngle, maxNumberOfRoadsPerJunction)
            pass
        
        # 3. create connections and junction

        junction = self.createJunctionForASeriesOfRoads(roads)

        odrName = 'Draw_Rmax' + str(maxNumberOfRoadsPerJunction) + '_L2_' + str(odrId)
        odr = extensions.createOdrByPredecessor(odrName, roads, [junction])

        # The last connection and resetting odr

        lastConnection = self.createLastConnectionForLastAndFirstRoad(nextRoadId, roads, junction, cp1=cp1)
        roads.append(lastConnection)
        odr.add_road(lastConnection)

        logging.debug(f"{self.name}: roads before internal connections {len(roads)}")

        if internalConnections:
            self.createInternalConnectionsForMissingSequentialRoads(roads, junction, cp1=cp1)
            odr.updateRoads(roads)

        logging.debug(f"{self.name}: roads after internal connections {len(roads)}")

        odr.resetAndReadjust(byPredecessor=True)
        
        return odr


    def createGeoConnectionRoad(self, action, newConnectionId, availableAngle, maxAnglePerConnection, maxLaneWidth):

        newConnection = None
        newConnection, availableAngle = self.createGeoConnectionCurve(availableAngle, maxAnglePerConnection, newConnectionId, curveType= StandardCurveTypes.LongArc, maxLaneWidth=maxLaneWidth)
        return newConnection, availableAngle


    def createGeoConnectionCurve(self, availableAngle, maxAnglePerConnection, newConnectionId, curveType, maxLaneWidth):

        angleBetweenEndpoints = self.getSomeAngle(availableAngle, maxAnglePerConnection)
        availableAngle -= angleBetweenEndpoints
        # curvature = StandardCurvature.getRandomValue()
        # curvature = AngleCurvatureMap.getCurvatureForJunction(angleBetweenEndpoints)
        curvature = AngleCurvatureMap.getMaxCurvatureAgainstMaxRoadWidth(angleBetweenEndpoints, maxLaneWidth=maxLaneWidth)

        currentLength = AngleCurvatureMap.getLength(angleBetweenEndpoints, curvature, curveType)
        if currentLength > self.maxConnectionLength:
            raise Exception(f"{self.name}: createGeoConnectionCurve current length is greater than max length")
        
        if np.random.choice([0, 1, 2, 3]) == 0: # 25% chance
            # create a long curve
            newLength = np.random.uniform(currentLength, self.maxConnectionLength)
            curvature = AngleCurvatureMap.getCurvatureForAngleBetweenRoadAndLength(angleBetweenEndpoints, newLength, curveType)
            logging.info(f"{self.name}: extending curve length")

        logging.debug(f"{self.name}: Curvature for angle {math.degrees(angleBetweenEndpoints)} is {curvature}")
        # if curvature < StandardCurvature.Medium.value:
        #     curvature = StandardCurvature.Medium.value

        newConnection = self.curveBuilder.create(newConnectionId, angleBetweenEndpoints, isJunction=True, curvature=curvature, curveType=curveType)
        return newConnection, availableAngle



    def getSomeAngle(self, availableAngle, maxAnglePerConnection):

        angle = (availableAngle * np.random.choice(10)) / 9

        
        if angle < self.minAngle:
            angle = self.minAngle

        if angle > maxAnglePerConnection:
            angle = maxAnglePerConnection
        return angle

    
    def actionAfterDrawingOne(self, currentRoads, availableAngle, maxNumberOfRoads):


        actions = ['straightLine', "curve", "spiral", "s"]
        
        if availableAngle < self.minAngle:
            return "end"
        
        if len(currentRoads) >= (maxNumberOfRoads * 2 - 1): # dont count connection roads
            return "end"
        
        return actions[np.random.choice(len(actions))]

    
    def createWithRandomLaneConfigurations(self, 
                                            straightRoadsPath, 
                                            odrId, 
                                            maxNumberOfRoadsPerJunction, 
                                            maxLanePerSide=2, 
                                            minLanePerSide=0, 
                                            internalConnections=True, 
                                            cp1=pyodrx.ContactPoint.end, 
                                            randomState=None,
                                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY, 
                                            uTurnLanes=1,
                                            restrictedLanes=False):
        """All the incoming roads, except for the first, will have their start endpoint connected to the junction.

        Args:
            straightRoadsPath ([type]): [description]
            odrId ([type]): [description]
            maxNumberOfRoadsPerJunction ([type]): [description]
            maxLanePerSide (int, optional): [description]. Defaults to 2.
            minLanePerSide (int, optional): [description]. Defaults to 0.
            internalConnections (bool, optional): [description]. Defaults to True.
            cp1 ([type], optional): [description]. Defaults to pyodrx.ContactPoint.start.
            randomState ([type], optional): [description]. Defaults to None.

        Raises:
            Exception: [description]

        Returns:
            [type]: [description]
        """

        if maxNumberOfRoadsPerJunction < 2:
            raise Exception("Please add more than 1 roads")

        if uTurnLanes > 1:
            raise Exception("U-turn from more than one lanes is not implemented")

        harvestedStraightRoads = extensions.getObjectsFromDill(straightRoadsPath)

        if randomState is not None:
            np.random.set_state(randomState)

        for key in harvestedStraightRoads:
            logging.debug(f"{self.name}: {key} has {len(harvestedStraightRoads[key])} number of roads")

        
        randomStraightRoads = [self.getRandomHarvestedStraightRoad(0, harvestedStraightRoads, maxLanePerSide, minLanePerSide) for i in range(maxNumberOfRoadsPerJunction)]

        outsideRoads = [] # all the incoming/outgoing roads in this junction
        geoConnectionRoads = [] # connections roads which are for geometric positions, having no lanes
        laneConnectionRoads = [] # connection roads that have lanes.
        roads = []

        if restrictedLanes:
            if cp1 == pyodrx.ContactPoint.end:
                roads.append(self.createRandomStraightRoad(0, maxLanePerSide=maxLanePerSide, minLanePerSide=minLanePerSide, skipEndpoint=pyodrx.ContactPoint.start)) # first road
            else:
                roads.append(self.createRandomStraightRoad(0, maxLanePerSide=maxLanePerSide, minLanePerSide=minLanePerSide, skipEndpoint=pyodrx.ContactPoint.end)) # first road
        else:
            roads.append(self.getRandomHarvestedStraightRoad(0, harvestedStraightRoads, maxLanePerSide, minLanePerSide)) # first road

        roads[0].id = 0
        outsideRoads.append(roads[0])


        availableAngle = 1.8 * np.pi # 360 degrees
        maxAnglePerConnection = availableAngle / maxNumberOfRoadsPerJunction
        action = self.actionAfterDrawingOne(roads, availableAngle, maxNumberOfRoadsPerJunction)
        nextRoadId = 1
        while (action != "end"):

            logging.debug(f"{self.name}: availableAngle {math.degrees(availableAngle)}, number of roads: {len(roads) / 2}")

            # 0. road id generation
            previousRoadId = nextRoadId - 1
            newConnectionId = nextRoadId
            nextRoadId += 1
            newRoadId = nextRoadId
            nextRoadId += 1

            # 1. create a road
            # newRoad = self.getRandomHarvestedStraightRoad(newRoadId, harvestedStraightRoads, maxLanePerSide, minLanePerSide)
            if restrictedLanes:
                newRoad = self.createRandomStraightRoad(newRoadId, maxLanePerSide, minLanePerSide, skipEndpoint=pyodrx.ContactPoint.end) 
            else:
                newRoad = self.getRandomHarvestedStraightRoad(newRoadId, harvestedStraightRoads, maxLanePerSide, minLanePerSide)

            outsideRoads.append(newRoad)

            # 2. create a new connection road
            prevCp = pyodrx.ContactPoint.start
            if len(roads) == 1: # first road
                prevCp = cp1

            prevLanes, nextLanes = self.laneBuilder.getClockwiseAdjacentLanes(roads[-1], prevCp, newRoad, pyodrx.ContactPoint.start)
            maxLaneWidth = max(len(prevLanes), len(nextLanes)) * self.laneWidth
            newConnection, availableAngle = self.createGeoConnectionRoad(action, newConnectionId, availableAngle, maxAnglePerConnection, maxLaneWidth=maxLaneWidth)
            geoConnectionRoads.append(newConnection)
            
            # 5 add new roads
            roads.append(newConnection)
            roads.append(newRoad)

            roads[previousRoadId].addExtendedSuccessor(newConnection, 0, pyodrx.ContactPoint.start)

            if newConnection.id == 1:
                newConnection.addExtendedPredecessor(roads[previousRoadId], 0 , cp1)
            else:
                newConnection.addExtendedPredecessor(roads[previousRoadId], 0 , pyodrx.ContactPoint.start)
            
            RoadLinker.createExtendedPredSuc(predRoad=newConnection, predCp=pyodrx.ContactPoint.end, sucRoad=newRoad, sucCP=pyodrx.ContactPoint.start)

            self.laneBuilder.createLanesForConnectionRoad(newConnection, roads[previousRoadId], newRoad)

            # 6 get next action
            action = self.actionAfterDrawingOne(roads, availableAngle, maxNumberOfRoadsPerJunction)
            pass
        
        # 3.0 fix outgoing lane numbers

        self.fixNumOutgoingLanes(outsideRoads, cp1)

        # 3. create connections and junction
        # TODO this is not correct anymore.
        # junction = self.createJunctionForASeriesOfRoads(roads)
        junction = pyodrx.Junction("singleConnectionsJunction", 0)

        odrName = 'Draw_Rmax' + str(maxNumberOfRoadsPerJunction) + '_L2_' + str(odrId)
        odr = extensions.createOdrByPredecessor(odrName, roads, [junction])

        # The last connection and resetting odr

        # lastConnection = self.createLastConnectionForLastAndFirstRoad(nextRoadId, roads, junction, cp1=cp1)
        # nextRoadId += 1
        # self.laneBuilder.createLanesForConnectionRoad(lastConnection, roads[-1], roads[0])
        # roads.append(lastConnection)

        # odr.add_road(lastConnection)
        
        logging.debug(f"{self.name}: roads before internal connections {len(roads)}")

        if internalConnections:
            internalConnections = self.connectionBuilder.createSingleLaneConnectionRoads(nextRoadId, outsideRoads, cp1, internalLinkStrategy)
            nextRoadId += len(internalConnections)
            roads += internalConnections
            odr.updateRoads(roads)

            # remove lanes from connection roads which are used for geometric positioning of roads 
            for geoRoad in geoConnectionRoads:
                geoRoad.clearLanes()

            # TODO create the junction
            self.addInternalConnectionsToJunction(junction, internalConnections)

        # U-Turns
        if uTurnLanes == 1:
            uTurnConnections = self.connectionBuilder.createUTurnConnectionRoads(nextRoadId, outsideRoads, cp1)
            nextRoadId += 1
            roads += uTurnConnections
            odr.updateRoads(roads)
            self.addInternalConnectionsToJunction(junction, internalConnections)


        logging.debug(f"{self.name}: roads after internal connections {len(roads)}")

        odr.resetAndReadjust(byPredecessor=True)
        
        
        return odr


    def fixNumOutgoingLanes(self, roads, cp1): 
        """Assumes all roads except the first road have start point in the intersection.

        Args:
            roads ([type]): outside roads for an intersection
            cp1 ([type]): contact point of the first road
        """

        roadDic = {}
        for road in roads:
            roadDic[road.id] = road


        firstRoadId = roads[0].id
        incomingLanes = []
        outgoingLanes = []
        cp = None
        for road in roads:

            if road.id == firstRoadId:
                cp = cp1
            else:
                cp = pyodrx.ContactPoint.start
            
            incomingLanes = LaneConfiguration.getIncomingLanesOnARoad(road, cp, self.countryCode)
            outgoingLaneIds = LaneConfiguration.getOutgoingLanesIdsFromARoad(road, roads, cp1, self.countryCode)


            diff = len(incomingLanes) - len(outgoingLaneIds) 
            if diff > 0:

                if len(outgoingLaneIds) == 0:
                    # special case when we have no outgoing lanes
                    if road.id != firstRoadId:
                        self.laneBuilder.addOutgoingLanes(roads[0], cp1, diff, self.countryCode, laneWidth=self.laneWidth)
                    else:
                        self.laneBuilder.addOutgoingLanes(roads[-1], pyodrx.ContactPoint.start, diff, self.countryCode, laneWidth=self.laneWidth)
                else:
                    # add necessary outgoing lanes to the first road with existing outgoing lanes
                    firstOutgoinRoadId = int(outgoingLaneIds[0].split(':')[0])
                    if firstOutgoinRoadId == firstRoadId:
                        self.laneBuilder.addOutgoingLanes(roads[0], cp1, diff, self.countryCode, laneWidth=self.laneWidth)
                    else:
                        self.laneBuilder.addOutgoingLanes(roadDic[firstOutgoinRoadId], pyodrx.ContactPoint.start, diff, self.countryCode, laneWidth=self.laneWidth)


            # now check if the road as lonely outgoing lanes, add one incoming lane to some other road if needed.
            outgoingLanes = LaneConfiguration.getOutgoingLanesOnARoad(road, cp, self.countryCode)
            incomingLaneIds = LaneConfiguration.getIncomingLanesIdsToARoad(road, roads, cp1, self.countryCode)

            if len(outgoingLanes) > 0 and len(incomingLaneIds) == 0:
                if len(incomingLaneIds) == 0:
                    # special case when we have no incoming lanes
                    if road.id != firstRoadId:
                        self.laneBuilder.addIncomingLanes(roads[0], cp1, 1, self.countryCode, laneWidth=self.laneWidth)
                    else:
                        self.laneBuilder.addIncomingLanes(roads[-1], pyodrx.ContactPoint.start, 1, self.countryCode, laneWidth=self.laneWidth)
                else:
                    firstIncomingRoadId = int(incomingLaneIds[0].split(':')[0])
                    if firstIncomingRoadId == firstRoadId:
                        self.laneBuilder.addIncomingLanes(roads[0], cp1, 1, self.countryCode, laneWidth=self.laneWidth)
                    else:
                        self.laneBuilder.addIncomingLanes(roadDic[firstIncomingRoadId], pyodrx.ContactPoint.start, 1, self.countryCode, laneWidth=self.laneWidth)



        pass


    def getRandomHarvestedStraightRoad(self, roadId, harvestedStraightRoads, maxLanePerSide=2, minLanePerSide=0):

        laneRange = np.arange(minLanePerSide, maxLanePerSide + 1)
        n_lanes_left = np.random.choice(laneRange)
        n_lanes_right = np.random.choice(laneRange)

        if (n_lanes_left == 0) and (n_lanes_right == 0):
            return self.getRandomHarvestedStraightRoad(roadId, harvestedStraightRoads, maxLanePerSide, minLanePerSide)

        odrs = harvestedStraightRoads[f"{n_lanes_left}-{n_lanes_right}"]
        logging.debug(f"{self.name}: getRandomHarvestedStraightRoad {n_lanes_left}-{n_lanes_right}")
        logging.debug(f"{self.name}: getRandomHarvestedStraightRoad{len(odrs)}")

        odr = odrs[np.random.choice(len(odrs))]

        for road in odr.roads.values():
            road = road.shallowCopy() # first road
            road.id = roadId
            return road
        
        raise Exception("No road found")

    def createRandomStraightRoad(self, roadId,  maxLanePerSide=2, minLanePerSide=0, withMedianRestricted=True, skipEndpoint=None):

        return self.straightRoadBuilder.createRandom(roadId, 
                                                        length=self.straightRoadLen,
                                                        junction=-1,
                                                        lane_offset=self.laneWidth,
                                                        maxLanePerSide=maxLanePerSide,
                                                        minLanePerSide=minLanePerSide,
                                                        medianType='partial',
                                                        medianWidth=self.laneWidth,
                                                        skipEndpoint=skipEndpoint)


    
    def addInternalConnectionsToJunction(self, junction, internalConnections):
        # NEed to implement it while creating the connection.
        
        # connectionLaneId = -1
        # if self.countryCode == CountryCodes.US:
        #     connectionLaneId = -1
        # elif self.countryCode == CountryCodes.UK:
        #     connectionLaneId = 1

        # for connectionRoad in internalConnections:
        #     extendedPred = connectionRoad.extendedPredecessors.values()[0]
        #     connectionL = pyodrx.Connection(extendedPred.road.id, connectionRoad.id, pyodrx.ContactPoint.start)
        #     connectionL.add_lanelink(connectionLaneId,-1)
        pass

    
    def getConnectionRoadsForSequentialRoads(self, roads):

        
        fromIndex = 1
        countOldRoads = len(roads)
        connectionRoads = []
        while fromIndex < countOldRoads:
            connectionRoad = roads[fromIndex]
            if connectionRoad.isConnection is False:
                raise Exception(f"getConnectionRoadsForSequentialRoads: road #{connectionRoad.id} is not a connection. Check if it's a sequentially generated junction.")
            connectionRoads.append(connectionRoad)
            fromIndex += 2
        
        return connectionRoads



    def createInternalConnectionsForMissingSequentialRoads(self, roads, junction, cp1 = pyodrx.ContactPoint.start, rebuildLanes=False):

        """Does not add connection to any junction. When are junction has all the roads connected to at least one connection road in a sequential manner, you can use
        this method to connect roads which are not already connected. 
        """


        # for first road:
        # fromId = 0
        # toId = roads[2].id
        # nextRoadId = roads[-1].id + 1
        # countOldRoads = len(roads)
        # while(toId < countOldRoads):
        #     connectionRoad = self.createConnectionFor2Roads(nextRoadId, roads[fromId], roads[toId], junction, cp1=cp1)
        #     roads.append(connectionRoad)
        #     toId += 2
        #     nextRoadId += 1

        newConnectionRoads = []        
        
        connectionRoads = self.getConnectionRoadsForSequentialRoads(roads)

        fromIndex = 0
        countOldRoads = len(roads)
        nextRoadId = roads[-1].id + 1

        while fromIndex < countOldRoads:
            toIndex = fromIndex + 4

            while toIndex < countOldRoads:
                if toIndex == fromIndex:
                    toIndex += 2
                    continue
                
                if RoadLinker.areRoadsConnected(roads[fromIndex], roads[toIndex], connectionRoads) is False:
                    if fromIndex == 0:
                        connectionRoad = self.createConnectionFor2Roads(nextRoadId, roads[fromIndex], roads[toIndex], junction, cp1=cp1, cp2=pyodrx.ContactPoint.start)
                    else:
                        connectionRoad = self.createConnectionFor2Roads(nextRoadId, roads[fromIndex], roads[toIndex], junction, cp1=pyodrx.ContactPoint.start, cp2=pyodrx.ContactPoint.start)
                    roads.append(connectionRoad)
                    newConnectionRoads.append(connectionRoad)
                    if rebuildLanes:
                        self.laneBuilder.createLanesForConnectionRoad(connectionRoad, roads[fromIndex], roads[toIndex])

                toIndex += 2
                nextRoadId += 1
                pass

            fromIndex += 2

        return newConnectionRoads        