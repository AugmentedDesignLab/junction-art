import pyodrx, math
from junctions.RoadBuilder import RoadBuilder
import numpy as np
import extensions
from junctions.LaneSides import LaneSides


class JunctionBuilder:
    

    def __init__(self, roadBuilder = None,
                straightRoadLen = 10,):


        self.roadBuilder = roadBuilder

        if self.roadBuilder is None:
            self.roadBuilder = RoadBuilder()

        self.straightRoadLen = straightRoadLen
        pass

    def createJunctionForASeriesOfRoads(self, roads):
        """[summary]

        Args:
            roads ([type]): even indices are roads, odd indices are connection roads  of the junction

        Returns:
            [type]: [description]
        """

        junction = pyodrx.Junction("spiderJunction", 0)

        connectionId = 1

        while (connectionId < len(roads)):

            print(f"connecting roads {connectionId-1} {connectionId}")
            connectionL = pyodrx.Connection(connectionId-1, connectionId, pyodrx.ContactPoint.start)
            connectionL.add_lanelink(-1,-1)

            # if (connectionId + 1) < len(roads):
            #     connectionR = pyodrx.Connection(connectionId+1, connectionId, pyodrx.ContactPoint.end)
            # else:
            #     connectionR = pyodrx.Connection(0, connectionId, pyodrx.ContactPoint.end)

            # connectionR.add_lanelink(1,1)

            junction.add_connection(connectionL)
            # junction.add_connection(connectionR)

            connectionId += 2
        
        return junction

    def createLastConnectionForLastAndFirstRoad(self, 
                                                nextRoadId, 
                                                roads, 
                                                junction, 
                                                cp1 = pyodrx.ContactPoint.end, 
                                                cp2 = pyodrx.ContactPoint.start
                                                ):

        lastConnectionId = nextRoadId + 100
        lastConnection = self.roadBuilder.getConnectionRoadBetween(lastConnectionId, roads[0], roads[-1], cp1, cp2)
        lastConnection.add_predecessor(pyodrx.ElementType.road, roads[-1].id, cp2)
        lastConnection.add_successor(pyodrx.ElementType.road, roads[0].id, cp1)

        roads[-1].add_successor(pyodrx.ElementType.junction, lastConnectionId, pyodrx.ContactPoint.start) 
        roads[0].add_predecessor(pyodrx.ElementType.junction, lastConnectionId, pyodrx.ContactPoint.end) 


        connectionL = pyodrx.Connection(roads[-1].id, lastConnectionId, pyodrx.ContactPoint.start)
        connectionL.add_lanelink(-1,-1)
        junction.add_connection(connectionL)
        
        roads.append(lastConnection)

        return lastConnection
    
    def createConnectionFor2Roads(self, 
                                    nextRoadId, 
                                    road1, 
                                    road2, 
                                    junction, 
                                    cp1 = pyodrx.ContactPoint.end, 
                                    cp2 = pyodrx.ContactPoint.start,
                                    n_lanes=1,
                                    lane_offset=3,
                                    laneSides=LaneSides.BOTH
                                    ):

        """Does not modify predecessor or successor of the given roads.

        Args:
            junction: the junction object to add links.

        Returns:
            [type]: connection road with first road as the predecessor and second road as the successor
        """


        lastConnectionId = nextRoadId
        lastConnection = self.roadBuilder.getConnectionRoadBetween(lastConnectionId, road1, road2, cp1, cp2,
                                    n_lanes=n_lanes,
                                    lane_offset=lane_offset,
                                    laneSides=laneSides)
        if road1.isConnection:
            lastConnection.updatePredecessor(pyodrx.ElementType.junction, road1.id, cp1)
        else:
            lastConnection.updatePredecessor(pyodrx.ElementType.road, road1.id, cp1)

            
        if road2.isConnection:
            lastConnection.updateSuccessor(pyodrx.ElementType.junction, road2.id, cp2)
        else:
            lastConnection.updateSuccessor(pyodrx.ElementType.road, road2.id, cp2)


        connectionL = pyodrx.Connection(road2.id, lastConnectionId, pyodrx.ContactPoint.start)
        connectionL.add_lanelink(-1,-1)
        junction.add_connection(connectionL)
        
        return lastConnection


    def createInternalConnectionsForOddIndices(self, roads, junction, cp1 = pyodrx.ContactPoint.start ):

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

        
        

        fromIndex = 0
        countOldRoads = len(roads)
        nextRoadId = roads[-1].id + 1

        while fromIndex < countOldRoads:
            toIndex = fromIndex + 4

            while toIndex < countOldRoads:
                if toIndex == fromIndex:
                    toIndex += 2
                    continue
                
                if fromIndex == 0:
                    connectionRoad = self.createConnectionFor2Roads(nextRoadId, roads[fromIndex], roads[toIndex], junction, cp1=cp1)
                else:
                    connectionRoad = self.createConnectionFor2Roads(nextRoadId, roads[fromIndex], roads[toIndex], junction)

                roads.append(connectionRoad)
                toIndex += 2
                nextRoadId += 1
                pass

            fromIndex += 2

        
        pass


    def buildSimpleRoundAbout(self, odrId=0, numRoads = 4, radius = 10, cp1 = pyodrx.ContactPoint.start):
        """In a simple roundabout, there is a circle inside the junction, the connection roads reside in the circle.

        Args:
            numRoads (int, optional): [description]. Defaults to 4.
            radius : in meters.
            cp1: contact point on the first road.
        """

        anglePerRoad = (np.pi * 2) / numRoads

        roads = []
        roads.append(pyodrx.create_straight_road(0, 10))
        nextRoadId = 1

        roadsCreated = 1

        connectionSeres = [] # holds all the connection road series so that we can create internal connections later.

        while roadsCreated < numRoads:
            previousRoadId = nextRoadId - 1
            newConnectionId = nextRoadId

            # 2. create a new connection road
            newConnectionSeries = self.roadBuilder.createRoundAboutConnection(newConnectionId, anglePerRoad, radius)
            connectionSeres.append(newConnectionSeries)

            nextRoadId += newConnectionSeries.length()
            newRoadId = nextRoadId
            nextRoadId += 1

            # 1. create a road
            newRoad = pyodrx.create_straight_road(newRoadId, self.straightRoadLen)

            
            # 5 add new roads and increase road id
            roads += newConnectionSeries.getAll()
            roads.append(newRoad)

            roads[previousRoadId].add_successor(pyodrx.ElementType.junction, newConnectionSeries.getFirst().id, pyodrx.ContactPoint.start)

            if newConnectionSeries.getFirst().id == 1 and cp1 == pyodrx.ContactPoint.end:
                newConnectionSeries.getFirst().add_predecessor(pyodrx.ElementType.road, previousRoadId, pyodrx.ContactPoint.end)
                # TODO this is a hack. It will not eventually work because outgoing roads' ends will come to join other junctions.
                # newConnectionSeries.getFirst().add_predecessor(pyodrx.ElementType.road, previousRoadId, pyodrx.ContactPoint.start)
            else:
                newConnectionSeries.getFirst().add_predecessor(pyodrx.ElementType.road, previousRoadId, pyodrx.ContactPoint.start)
            
            newConnectionSeries.getLast().add_successor(pyodrx.ElementType.road, newRoad.id, pyodrx.ContactPoint.start) 
            newRoad.add_predecessor(pyodrx.ElementType.junction, newConnectionSeries.getLast().id, pyodrx.ContactPoint.end)


            # 6 get next action
            roadsCreated += 1

            pass
        # 3. create connections and junction

        junction = self.createJunctionForASeriesOfRoads(roads)

        # print(f"number of roads created {len(roads)}")
        odrName = 'Simple-Roundabout-' + str(numRoads) + '_L2_' + str(odrId)
        odr = extensions.createOdrByPredecessor(odrName, roads, [junction])

        # The last connection and resetting odr

        newConnectionSeries = self.roadBuilder.createRoundAboutConnection(nextRoadId, anglePerRoad, radius)
        connectionSeres.append(newConnectionSeries)

        roads += newConnectionSeries.getAll()
        newConnectionSeries.getFirst().add_predecessor(pyodrx.ElementType.road, nextRoadId-1, pyodrx.ContactPoint.start)

        if cp1 == pyodrx.ContactPoint.end:
            newConnectionSeries.getLast().add_successor(pyodrx.ElementType.road, 0, pyodrx.ContactPoint.end)
            # TODO this is a hack. It will not eventually work because outgoing roads' ends will come to join other junctions.
            # newConnection.add_predecessor(pyodrx.ElementType.road, previousRoadId, pyodrx.ContactPoint.start)
        else:
            newConnectionSeries.getLast().add_successor(pyodrx.ElementType.road, 0, pyodrx.ContactPoint.start)
            
        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)

        # Last step, link connection series by curves

        self.createInternalConnectionsForConnectionSeres(roads, connectionSeres, junction)

        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)

        return odr
        

    def createInternalConnectionsForConnectionSeres(self, roads, connectionSeres, junction):
        """Assumes last road has the largest id.

        Args:
            roads ([type]): [description]
            connectionSeres ([type]): [description]
        """


        # for each last road in a series, connect with the next first road
        length = len(connectionSeres)
        nextRoadId = connectionSeres[-1].getLast().id + 1 # last id so far.

        for i in range(length):
            currentConnectionS = connectionSeres[i]

            if (i + 1) < length:
                nextConnectionS = connectionSeres[i + 1]
            else:
                nextConnectionS = connectionSeres[0]

            # traffic will go from current to next

            newConnection = self.createConnectionFor2Roads(
                nextRoadId,
                currentConnectionS.getLast(), 
                nextConnectionS.getFirst(), 
                junction=junction, 
                laneSides=LaneSides.LEFT)
            
            roads.append(newConnection)

            nextRoadId += 1
        
        return nextRoadId
            

            
