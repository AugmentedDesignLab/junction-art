import pyodrx
from junctions.RoadBuilder import RoadBuilder


class JunctionBuilder:
    

    def __init__(self, roadBuilder = None):


        self.roadBuilder = roadBuilder

        if self.roadBuilder is None:
            self.roadBuilder = RoadBuilder()

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
                                    cp2 = pyodrx.ContactPoint.start
                                    ):

        """Does not modifer predecessor or successor of the given roads.

        Returns:
            [type]: [description]
        """

        lastConnectionId = nextRoadId + 100
        lastConnection = self.roadBuilder.getConnectionRoadBetween(lastConnectionId, road1, road2, cp1, cp2)
        lastConnection.add_predecessor(pyodrx.ElementType.road, road2.id, cp2)
        lastConnection.add_successor(pyodrx.ElementType.road, road1.id, cp1)

        # road2.add_successor(pyodrx.ElementType.junction, lastConnectionId, pyodrx.ContactPoint.start) 
        # road1.add_predecessor(pyodrx.ElementType.junction, lastConnectionId, pyodrx.ContactPoint.end) 


        connectionL = pyodrx.Connection(road2.id, lastConnectionId, pyodrx.ContactPoint.start)
        connectionL.add_lanelink(-1,-1)
        junction.add_connection(connectionL)
        
        return lastConnection
