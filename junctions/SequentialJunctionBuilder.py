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


class SequentialJunctionBuilder(JunctionBuilder):
    

    def drawLikeAPainter2L(self, odrId, maxNumberOfRoadsPerJunction, save=True, internalConnections=True, cp1=pyodrx.ContactPoint.end):
        if maxNumberOfRoadsPerJunction < 3:
            raise Exception("drawLikeAPainter is not for the weak. Please add more than 3 roads")

        roads = []
        roads.append(self.straightRoadBuilder.create(0, length=self.straightRoadLen * 4)) # first road

        availableAngle = 1.8 * np.pi # 360 degrees
        maxAnglePerConnection = availableAngle / (maxNumberOfRoadsPerJunction - 1)
        action = self.actionAfterDrawingOne(roads, availableAngle, maxNumberOfRoadsPerJunction)
        nextRoadId = 1
        while (action != "end"):

            print(f"availableAngle {math.degrees(availableAngle)}, number of roads: {len(roads) / 2}")
            previousRoadId = nextRoadId - 1
            newConnectionId = nextRoadId
            nextRoadId += 1
            newRoadId = nextRoadId
            nextRoadId += 1

            # 1. create a road
            newRoad = self.straightRoadBuilder.create(newRoadId, length=self.straightRoadLen)

            # 2. create a new connection road
            newConnection, availableAngle = self.createNewConnectionForDrawing(action, newConnectionId, availableAngle, maxAnglePerConnection)
            
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

        # print(f"number of roads created {len(roads)}")
        odrName = 'Draw_Rmax' + str(maxNumberOfRoadsPerJunction) + '_L2_' + str(odrId)
        odr = extensions.createOdrByPredecessor(odrName, roads, [junction])

        # The last connection and resetting odr

        lastConnection = self.createLastConnectionForLastAndFirstRoad(nextRoadId, roads, junction, cp1=cp1)
        odr.add_road(lastConnection)

        print(f"roads before internal connections {len(roads)}")

        if internalConnections:
            self.createInternalConnectionsForMissingSequentialRoads(roads, junction, cp1=cp1)
            odr.updateRoads(roads)

        print(f"roads after internal connections {len(roads)}")

        odr.resetAndReadjust(byPredecessor=True)
        
        return odr


    def createNewConnectionForDrawing(self, action, newConnectionId, availableAngle, maxAnglePerConnection):

        newConnection = None
        newConnection, availableAngle = self.createCurveForDrawing(availableAngle, maxAnglePerConnection, newConnectionId, curveType= StandardCurveTypes.LongArc)
        return newConnection, availableAngle
        # if action is 'straightLine':
        #     newConnection = pyodrx.create_straight_road(newConnectionId, self.straightRoadLen, junction=1)
        #     availableAngle -= np.pi
        # elif action is 'curve':
        #     newConnection, availableAngle = self.createCurveForDrawing(availableAngle, maxAnglePerConnection, newConnectionId, curveType= StandardCurveTypes.LongArc)
        # elif action is 'spiral':
        #     newConnection, availableAngle = self.createCurveForDrawing(availableAngle,maxAnglePerConnection,  newConnectionId, curveType= StandardCurveTypes.Simple)
        # elif action is 's':
        #     newConnection, availableAngle = self.createCurveForDrawing(availableAngle, maxAnglePerConnection, newConnectionId, curveType= StandardCurveTypes.S)

        # return newConnection, availableAngle


    def createCurveForDrawing(self, availableAngle, maxAnglePerConnection, newConnectionId, curveType):
        angleBetweenEndpoints = self.getSomeAngle(availableAngle, maxAnglePerConnection)
        availableAngle -= angleBetweenEndpoints
        # curvature = StandardCurvature.getRandomValue()
        curvature = AngleCurvatureMap.getCurvatureForJunction(angleBetweenEndpoints)

        print(f"Curvature for angle {math.degrees(angleBetweenEndpoints)} is {curvature}")
        # if curvature < StandardCurvature.Medium.value:
        #     curvature = StandardCurvature.Medium.value

        newConnection = self.roadBuilder.createCurve(newConnectionId, angleBetweenEndpoints, isJunction=True, curvature=curvature, curveType=curveType)
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

    
    def createWithRandomLaneConfigurations(self, straightRoadsPath, odrId, maxNumberOfRoadsPerJunction, maxLanePerSide=2, internalConnections=True, cp1=pyodrx.ContactPoint.start, randomState=None):

        if not os.path.isfile(straightRoadsPath):
            raise Exception(f"{straightRoadsPath} does not exist")

        harvestedStraightRoads = None
        if randomState is not None:
            np.random.set_state(randomState)

        with open(straightRoadsPath, "rb") as f:
            harvestedStraightRoads = dill.load(f)

        for key in harvestedStraightRoads:
            print(f"{key} has {len(harvestedStraightRoads[key])} number of roads")

        if maxNumberOfRoadsPerJunction < 2:
            raise Exception("Please add more than 1 roads")

        roads = []
        roads.append(self.getRandomStraightRoad(0, harvestedStraightRoads, maxLanePerSide)) # first road
        roads[0].id = 0

        availableAngle = 1.8 * np.pi # 360 degrees
        maxAnglePerConnection = availableAngle / (maxNumberOfRoadsPerJunction - 1)
        action = self.actionAfterDrawingOne(roads, availableAngle, maxNumberOfRoadsPerJunction)
        nextRoadId = 1
        while (action != "end"):

            print(f"availableAngle {math.degrees(availableAngle)}, number of roads: {len(roads) / 2}")
            previousRoadId = nextRoadId - 1
            newConnectionId = nextRoadId
            nextRoadId += 1
            newRoadId = nextRoadId
            nextRoadId += 1

            # 1. create a road
            newRoad = self.getRandomStraightRoad(newRoadId, harvestedStraightRoads, maxLanePerSide)

            # 2. create a new connection road
            newConnection, availableAngle = self.createNewConnectionForDrawing(action, newConnectionId, availableAngle, maxAnglePerConnection)
            
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

        # print(f"number of roads created {len(roads)}")
        odrName = 'Draw_Rmax' + str(maxNumberOfRoadsPerJunction) + '_L2_' + str(odrId)
        odr = extensions.createOdrByPredecessor(odrName, roads, [junction])

        # The last connection and resetting odr

        lastConnection = self.createLastConnectionForLastAndFirstRoad(nextRoadId, roads, junction, cp1=cp1)
        odr.add_road(lastConnection)

        print(f"roads before internal connections {len(roads)}")

        if internalConnections:
            self.createInternalConnectionsForMissingSequentialRoads(roads, junction, cp1=cp1)
            odr.updateRoads(roads)

        print(f"roads after internal connections {len(roads)}")

        odr.resetAndReadjust(byPredecessor=True)
        
        return odr


    def getRandomStraightRoad(self, roadId, harvestedStraightRoads, maxLanePerSide=2):

        n_lanes_left = np.random.choice(maxLanePerSide + 1)
        n_lanes_right = np.random.choice(maxLanePerSide + 1)

        if (n_lanes_left == 0) and (n_lanes_right == 0):
            return self.getRandomStraightRoad(roadId, harvestedStraightRoads, maxLanePerSide)

        odrs = harvestedStraightRoads[f"{n_lanes_left}-{n_lanes_right}"]
        print(f"{n_lanes_left}-{n_lanes_right}")
        print(len(odrs))

        odr = odrs[np.random.choice(len(odrs))]

        for road in odr.roads.values():
            road = road.shallowCopy() # first road
            road.id = roadId
            return road
        
        raise Exception("No road found")



    
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



    def createInternalConnectionsForMissingSequentialRoads(self, roads, junction, cp1 = pyodrx.ContactPoint.start ):

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

                toIndex += 2
                nextRoadId += 1
                pass

            fromIndex += 2

        
        pass