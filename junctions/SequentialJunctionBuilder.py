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
from junctions.Intersection import Intersection
from junctions.JunctionDef import JunctionDef
import logging


class SequentialJunctionBuilder(JunctionBuilder):

    def __init__(self, roadBuilder = None,
                straightRoadLen = 10,
                minAngle = np.pi/6, 
                maxAngle = None, 
                country=CountryCodes.US, 
                random_seed=39,
                minConnectionLength=None,
                maxConnectionLength=None,
                probMinAngle=None,
                probLongConnection=None,
                probRestrictedLane=None
                ):
            
        super().__init__(roadBuilder=roadBuilder,
                        straightRoadLen=straightRoadLen,
                        minAngle=minAngle,
                        maxAngle=maxAngle,
                        country=country,
                        random_seed=random_seed
                        )
        self.name = 'SequentialJunctionBuilder'
        self.probMinAngle = self.config.get('probability_min_angle')
        self.probLongConnection = self.config.get('probability_long_connection')
        self.probRestrictedLane = self.config.get('probability_restricted_lane')

        if minConnectionLength is not None:
            self.minConnectionLength = minConnectionLength
        if maxConnectionLength is not None:
            self.maxConnectionLength = maxConnectionLength
        if probMinAngle is not None:
            self.probMinAngle = probMinAngle
        if probLongConnection is not None:
            self.probLongConnection = probLongConnection
        if probRestrictedLane is not None:
            self.probRestrictedLane = probRestrictedLane
    

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

        junction = self.createJunctionForASeriesOfRoads(roads, odrId)

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


    def createGeoConnectionRoad(self, action, newConnectionId, availableAngle, maxAnglePerConnection, maxLaneWidth, equalAngles=False):

        newConnection = None
        newConnection, availableAngle = self.createGeoConnectionCurve(availableAngle, maxAnglePerConnection, newConnectionId, curveType= StandardCurveTypes.LongArc, maxLaneWidth=maxLaneWidth, equalAngles=equalAngles)
        return newConnection, availableAngle


    def createGeoConnectionCurve(self, availableAngle, maxAnglePerConnection, newConnectionId, curveType, maxLaneWidth, equalAngles=False):
        
        angleBetweenEndpoints = maxAnglePerConnection
        if not equalAngles:
            angleBetweenEndpoints = self.getSomeAngle(availableAngle, maxAnglePerConnection)

        availableAngle -= angleBetweenEndpoints
        
        curvature = AngleCurvatureMap.getMaxCurvatureAgainstMaxRoadWidth(angleBetweenEndpoints, maxLaneWidth=maxLaneWidth)

        currentLength = AngleCurvatureMap.getLength(angleBetweenEndpoints, curvature, curveType)
        if currentLength > self.maxConnectionLength:
            raise Exception(f"{self.name}: createGeoConnectionCurve current length {currentLength} is greater than max length {self.maxConnectionLength}")
        
        # make a long safe connection
        if availableAngle > np.pi :
            if np.random.choice([True, False], p=[self.probLongConnection, 1 - self.probLongConnection]): 
                # create a long curve
                currentLength = np.random.uniform(currentLength, self.maxConnectionLength)
                curvature = AngleCurvatureMap.getCurvatureForAngleBetweenRoadAndLength(angleBetweenEndpoints, currentLength, curveType)
                logging.info(f"{self.name}: extending curve length")
        # print(f"curve length: {currentLength}") 
        if currentLength < self.minConnectionLength:
            # raise Exception(f"{self.name}: createGeoConnectionCurve current length {currentLength} is less than min length {self.minConnectionLength}")
            currentLength = self.minConnectionLength
            curvature = AngleCurvatureMap.getCurvatureForAngleBetweenRoadAndLength(angleBetweenEndpoints, currentLength, curveType)
            logging.info(f"{self.name}: extending curve length to min length {self.minConnectionLength}")


        logging.debug(f"{self.name}: Curvature for angle {math.degrees(angleBetweenEndpoints)} is {curvature}")
        
        newConnection = self.curveBuilder.create(newConnectionId, angleBetweenEndpoints, isJunction=True, curvature=curvature, curveType=curveType)
        return newConnection, availableAngle



    def getSomeAngle(self, availableAngle, maxAnglePerConnection):

        # print(f"minAngle: {math.degrees(self.minAngle)}, available Angle: {math.degrees(availableAngle)}")

        if availableAngle <= 0:
            raise Exception(f"{self.name}: getSomeAngle: no available angle")

        if np.random.choice([True, False], p=[self.probMinAngle, 1-self.probMinAngle]):
            modifier = np.random.uniform(-0.1, 0.1)
            return self.minAngle + (self.minAngle * modifier)

        if self.minAngle >= availableAngle:
            return availableAngle

        # maxAngle = (maxAnglePerConnection + availableAngle) / 2
        # if maxAngle > availableAngle:
        #     maxAngle = availableAngle

        angle = np.random.uniform(self.minAngle, availableAngle)
        # angle = np.random.uniform(self.minAngle, maxAngle)
        # angle = np.random.uniform(self.minAngle, availableAngle)
        # angle = (availableAngle * np.random.choice(10)) / 9

        

        if self.maxAngle is not None:

            if angle > self.maxAngle:
                angle = self.maxAngle
        elif angle > maxAnglePerConnection:
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
                                            id, 
                                            maxNumberOfRoadsPerJunction, 
                                            firstRoadId=0,
                                            maxLanePerSide=2, 
                                            minLanePerSide=0, 
                                            internalConnections=True, 
                                            cp1=pyodrx.ContactPoint.end, 
                                            randomState=None,
                                            internalLinkStrategy = LaneConfigurationStrategies.SPLIT_ANY, 
                                            uTurnLanes=1,
                                            equalAngles=False,
                                            getAsOdr=True):
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

        harvestedStraightRoads = []

        # if restrictedLanes:
        #     harvestedStraightRoads = []
        # else:
        #     harvestedStraightRoads = extensions.getObjectsFromDill(straightRoadsPath)

        if randomState is not None:
            np.random.set_state(randomState)

        incidentContactPoints = []
        outsideRoads = [] # all the incoming/outgoing roads in this junction
        geoConnectionRoads = [] # connections roads which are for geometric positions, having no lanes
        laneConnectionRoads = [] # connection roads that have lanes.
        roads = []

        if cp1 == pyodrx.ContactPoint.end:
            roads.append(self.createRandomStraightRoad(0, maxLanePerSide=maxLanePerSide, minLanePerSide=minLanePerSide, skipEndpoint=pyodrx.ContactPoint.start)) # first road
        else:
            roads.append(self.createRandomStraightRoad(0, maxLanePerSide=maxLanePerSide, minLanePerSide=minLanePerSide, skipEndpoint=pyodrx.ContactPoint.end)) # first road
        

        # if restrictedLanes:
        #     if cp1 == pyodrx.ContactPoint.end:
        #         roads.append(self.createRandomStraightRoad(0, maxLanePerSide=maxLanePerSide, minLanePerSide=minLanePerSide, skipEndpoint=pyodrx.ContactPoint.start)) # first road
        #     else:
        #         roads.append(self.createRandomStraightRoad(0, maxLanePerSide=maxLanePerSide, minLanePerSide=minLanePerSide, skipEndpoint=pyodrx.ContactPoint.end)) # first road
        # else:
        #     roads.append(self.getRandomHarvestedStraightRoad(0, harvestedStraightRoads, maxLanePerSide, minLanePerSide)) # first road

        # junctionId = id
        # firstRoadId += 1

        roads[0].id = firstRoadId
        roads[0].junctionCP = cp1
        roads[0].junctionRelation = 'successor'
        outsideRoads.append(roads[0])
        incidentContactPoints.append(cp1)

        availableAngle = 1.8 * np.pi # 360 degrees
        if equalAngles:
            availableAngle = np.pi * 2
        maxAnglePerConnection = availableAngle / maxNumberOfRoadsPerJunction
        action = self.actionAfterDrawingOne(roads, availableAngle, maxNumberOfRoadsPerJunction)
        nextRoadId = firstRoadId + 1
        otherContactPoints = pyodrx.ContactPoint.start
        nIncidentAdded = 1
        while (action != "end"):

            logging.debug(f"{self.name}: availableAngle {math.degrees(availableAngle)}, number of roads: {len(roads) / 2}")

            # 0. road id generation
            previousRoadId = nextRoadId - 1
            prevIncidentRoad = roads[-1]
            newConnectionId = nextRoadId
            nextRoadId += 1
            newRoadId = nextRoadId
            nextRoadId += 1
            prevCp = otherContactPoints
            if len(roads) == 1: # first road
                prevCp = cp1

            # 1. create a road
            # newRoad = self.getRandomHarvestedStraightRoad(newRoadId, harvestedStraightRoads, maxLanePerSide, minLanePerSide)
            newRoad = self.createRandomStraightRoad(newRoadId, maxLanePerSide, minLanePerSide, skipEndpoint=pyodrx.ContactPoint.end) 
            newRoad.junctionCP = otherContactPoints
            newRoad.junctionRelation = 'predecessor'
            # if restrictedLanes:
            #     newRoad = self.createRandomStraightRoad(newRoadId, maxLanePerSide, minLanePerSide, skipEndpoint=pyodrx.ContactPoint.end) 
            # else:
            #     newRoad = self.getRandomHarvestedStraightRoad(newRoadId, harvestedStraightRoads, maxLanePerSide, minLanePerSide)

            outsideRoads.append(newRoad)
            incidentContactPoints.append(otherContactPoints)

            # 2. create a new connection road

            prevLanes, nextLanes = self.laneBuilder.getClockwiseAdjacentLanes(prevIncidentRoad, prevCp, newRoad, otherContactPoints)
            # maxLaneWidth = ((len(prevLanes) + len(nextLanes)) * self.laneWidth) / 2
            maxLaneWidth = max(len(prevLanes), len(nextLanes)) * self.laneWidth
            if len(prevLanes) == 0 or len(nextLanes) == 0:
                maxLaneWidth = ((len(prevLanes) + len(nextLanes)) * self.laneWidth) / 2

            availableAngle -= (maxNumberOfRoadsPerJunction - nIncidentAdded - 1) * self.minAngle
            # print(f"Before connection road: minAngle: remaining roads:{maxNumberOfRoadsPerJunction - nIncidentAdded - 1}, {math.degrees(self.minAngle)}, available Angle: {math.degrees(availableAngle)}")

            newConnection, availableAngle = self.createGeoConnectionRoad(action, newConnectionId, availableAngle, maxAnglePerConnection, maxLaneWidth=maxLaneWidth, equalAngles=equalAngles)
            geoConnectionRoads.append(newConnection)

            availableAngle += (maxNumberOfRoadsPerJunction - nIncidentAdded - 1) * self.minAngle
            # print(f"after connection road: minAngle: {math.degrees(self.minAngle)}, available Angle: {math.degrees(availableAngle)}")
            
            # 5 add new roads
            roads.append(newConnection)
            roads.append(newRoad)
            
            RoadLinker.createExtendedPredSuc(predRoad=prevIncidentRoad, predCp=prevCp, sucRoad=newConnection, sucCP=pyodrx.ContactPoint.start)
            RoadLinker.createExtendedPredSuc(predRoad=newConnection, predCp=pyodrx.ContactPoint.end, sucRoad=newRoad, sucCP=otherContactPoints)

            self.laneBuilder.createLanesForConnectionRoad(newConnection, prevIncidentRoad, newRoad)

            # 6 get next action
            action = self.actionAfterDrawingOne(roads, availableAngle, maxNumberOfRoadsPerJunction)
            nIncidentAdded += 1
            pass
        
        # 3.0 fix outgoing lane numbers

        self.fixNumOutgoingLanes(outsideRoads, cp1)

        # 3. create connections and junction
        # TODO this is not correct anymore.
        # junction = self.createJunctionForASeriesOfRoads(roads)
        # junction = pyodrx.Junction("singleConnectionsJunction", junctionId)
        # junction = pyodrx.Junction("singleConnectionsJunction", firstRoadId)

        odrName = 'Draw_Rmax' + str(maxNumberOfRoadsPerJunction) + '_L2_' + str(id)
        odr = extensions.createOdrByPredecessor(odrName, roads, [])

        
        logging.debug(f"{self.name}: roads before internal connections {len(roads)}")


        connectionRoads = []

        # Permanent connection roads
        if internalConnections:
            internalConnections = self.connectionBuilder.createSingleLaneConnectionRoads(nextRoadId, outsideRoads, cp1, internalLinkStrategy)
            nextRoadId += len(internalConnections)
            roads += internalConnections
            odr.updateRoads(roads)

            # remove lanes from connection roads which are used for geometric positioning of roads 
            for geoRoad in geoConnectionRoads:
                geoRoad.clearLanes()

            # TODO create the junction
            # self.addInternalConnectionsToJunction(junction, internalConnections)
            connectionRoads += internalConnections

        # U-Turns
        if uTurnLanes == 1:
            uTurnConnections = self.connectionBuilder.createUTurnConnectionRoads(nextRoadId, outsideRoads, cp1)
            nextRoadId += len(uTurnConnections)
            roads += uTurnConnections
            odr.updateRoads(roads)
            # self.addInternalConnectionsToJunction(junction, internalConnections)
            connectionRoads += uTurnConnections


        # junction creation

        junction = JunctionDef(nextRoadId).build(connectionRoads)


        logging.debug(f"{self.name}: roads after internal connections {len(roads)}")

        odr.resetAndReadjust(byPredecessor=True)
        odr.add_junction(junction)

        if getAsOdr:
            return odr

        intersection = Intersection(id, outsideRoads, incidentContactPoints, geoConnectionRoads=geoConnectionRoads, odr=odr)
        return intersection


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

    def createRandomStraightRoad(self, roadId,  maxLanePerSide=2, minLanePerSide=0, skipEndpoint=None):

        medianType='partial'
        withMedianRestricted = np.random.choice([True, False], p=[self.probRestrictedLane, 1- self.probRestrictedLane]) 
        if not withMedianRestricted:
            medianType = None

        return self.straightRoadBuilder.createRandom(roadId, 
                                                        length=self.straightRoadLen,
                                                        junction=-1,
                                                        lane_offset=self.laneWidth,
                                                        maxLanePerSide=maxLanePerSide,
                                                        minLanePerSide=minLanePerSide,
                                                        medianType=medianType,
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
            if not connectionRoad.isConnection:
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
                
                if not RoadLinker.areRoadsConnected(roads[fromIndex], roads[toIndex], connectionRoads):
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