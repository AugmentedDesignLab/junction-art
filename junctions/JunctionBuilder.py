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
from junctions.LaneBuilder import LaneBuilder
from junctions.CurveRoadBuilder import CurveRoadBuilder
from extensions.CountryCodes import CountryCodes
from junctions.ConnectionBuilder import ConnectionBuilder
from library.Configuration import Configuration

class JunctionBuilder:
    

    def __init__(self, roadBuilder = None,
                straightRoadLen = 10,
                minAngle = np.pi/6, maxAngle = 1.8 * np.pi, country=CountryCodes.US, random_seed=39):

        self.config = Configuration()
        self.roadBuilder = roadBuilder

        if self.roadBuilder is None:
            self.roadBuilder = RoadBuilder()

        self.straightRoadBuilder = StraightRoadBuilder()
        self.laneBuilder = LaneBuilder()

        self.straightRoadLen = straightRoadLen

        self.minAngle = minAngle
        self.maxAngle = maxAngle
        self.laneWidth = self.config.get("default_lane_width")
        self.curveBuilder = CurveRoadBuilder(country=country)
        self.connectionBuilder = ConnectionBuilder()
        self.countryCode = country
        np.random.seed(random_seed)
        pass

    def createJunctionForASeriesOfRoads(self, roads):
        """[summary]

        Args:
            roads ([type]): even indices are roads, odd indices are connection roads  of the junction

        Returns:
            [type]: [description]
        """

        # TODO it does not support all lanes.
        # ID is wrong
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

        lastConnectionId = nextRoadId
        lastConnection = self.roadBuilder.getConnectionRoadBetween(lastConnectionId, roads[-1], roads[0], cp2, cp1)

        RoadLinker.createExtendedPredSuc(predRoad=roads[-1], predCp=cp2, sucRoad=lastConnection, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=lastConnection, predCp=pyodrx.ContactPoint.end, sucRoad=roads[0], sucCP=cp1)


        connectionL = pyodrx.Connection(roads[-1].id, lastConnectionId, pyodrx.ContactPoint.start)
        connectionL.add_lanelink(-1,-1)
        junction.add_connection(connectionL)
        
        # roads.append(lastConnection) # dangerous. do not add the road

        return lastConnection
    
    def createConnectionFor2Roads(self, 
                                    nextRoadId, 
                                    road1, 
                                    road2, 
                                    junction, 
                                    cp1,
                                    cp2,
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


        newConnectionId = nextRoadId
        newConnectionRoad = self.roadBuilder.getConnectionRoadBetween(newConnectionId, road1, road2, cp1, cp2,
                                    isJunction=True,
                                    n_lanes=n_lanes,
                                    lane_offset=lane_offset,
                                    laneSides=laneSides)
        
        RoadLinker.createExtendedPredSuc(predRoad=road1, predCp=cp1, sucRoad=newConnectionRoad, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=newConnectionRoad, predCp=pyodrx.ContactPoint.end, sucRoad=road2, sucCP=cp2)

        if junction is not None:
            if laneSides == LaneSides.LEFT or laneSides == LaneSides.BOTH:
                connectionL = pyodrx.Connection(road2.id, newConnectionId, pyodrx.ContactPoint.end)
                connectionL.add_lanelink(-1,-1)
                junction.add_connection(connectionL)
            else:
                connectionL = pyodrx.Connection(road1.id, newConnectionId, pyodrx.ContactPoint.start)
                connectionL.add_lanelink(1, 1)
                junction.add_connection(connectionL)
        
        return newConnectionRoad



    def createInternalConnectionsForConnectionSeres(self, roads, connectionSeres, junction):
        """Assumes last road has the largest id. Used to create internal connections inside a junction. Assumes a connection series has middle roads which are connected by an internal connection road. Normally each series will have 3 roads.

        Args:
            roads ([type]): [description]
            connectionSeres ([type]): list of ConnectionSeries type
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

            fromRoad = currentConnectionS.getMiddle()
            toRoad = nextConnectionS.getMiddle()

            print(f"creating internal connection from {fromRoad.id} to {toRoad.id}")

            newConnection = self.createConnectionFor2Roads(
                nextRoadId,
                fromRoad, 
                toRoad, 
                cp1=pyodrx.ContactPoint.end,
                cp2=pyodrx.ContactPoint.start,
                junction=junction, 
                laneSides=LaneSides.RIGHT)
            
            roads.append(newConnection)

            nextRoadId += 1
        
        return nextRoadId

    def buildSimpleRoundAbout(self, odrId=0, numRoads = 4, radius = 10, cp1 = pyodrx.ContactPoint.start, direction=CircularDirection.COUNTERCLOCK_WISE):
        """In a simple roundabout, there is a circle inside the junction, the connection roads reside in the circle.

        Args:
            numRoads (int, optional): [description]. Defaults to 4.
            radius : in meters.
            cp1: contact point on the first road.
        """

        anglePerRoad = (np.pi * 2) / numRoads

        roads = []
        roads.append(self.straightRoadBuilder.create(0, length=self.straightRoadLen))
        nextRoadId = 1

        roadsCreated = 1

        connectionSeres = [] # holds all the connection road series so that we can create internal connections later.

        while roadsCreated < numRoads:
            previousRoadId = nextRoadId - 1
            newConnectionId = nextRoadId

            # 1. create a new connection road series and increase nextRoadId
            newConnectionSeries = self.roadBuilder.createRoundAboutConnection(newConnectionId, anglePerRoad, radius)
            connectionSeres.append(newConnectionSeries)

            nextRoadId += newConnectionSeries.length()
            newRoadId = nextRoadId
            nextRoadId += 1

            # 2. create a road
            newRoad = self.straightRoadBuilder.create(newRoadId, length=self.straightRoadLen)
            
            # 3 add new roads 
            roads += newConnectionSeries.getAll()
            roads.append(newRoad)

            roads[previousRoadId].addExtendedSuccessor(newConnectionSeries.getFirst(), 0, pyodrx.ContactPoint.start)

            if newConnectionSeries.getFirst().id == 1:
                newConnectionSeries.getFirst().addExtendedPredecessor(roads[previousRoadId], 0, cp1)
                # TODO this is a hack. It will not eventually work because outgoing roads' ends will come to join other junctions.
            else:
                newConnectionSeries.getFirst().addExtendedPredecessor(roads[previousRoadId], 0, pyodrx.ContactPoint.start)
            
            RoadLinker.createExtendedPredSuc(predRoad=newConnectionSeries.getLast(), predCp=pyodrx.ContactPoint.end, sucRoad=newRoad, sucCP= pyodrx.ContactPoint.start)


            # 6 get next action
            roadsCreated += 1

            pass

        lastRoad = roads[-1]
        # 3. create connections and junction

        junction = self.createJunctionForASeriesOfRoads(roads)

        # print(f"number of roads created {len(roads)}")
        odrName = 'Simple-Roundabout-' + str(numRoads) + '_L2_' + str(odrId)
        odr = extensions.createOdrByPredecessor(odrName, roads, [junction])

        # The last connection and resetting odr

        finalConnectionSeries = self.roadBuilder.createRoundAboutConnection(nextRoadId, anglePerRoad, radius)
        connectionSeres.append(finalConnectionSeries)

        roads += finalConnectionSeries.getAll()
        
        RoadLinker.createExtendedPredSuc(predRoad=lastRoad, predCp=pyodrx.ContactPoint.start, sucRoad=finalConnectionSeries.getFirst(), sucCP= pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=finalConnectionSeries.getLast(), predCp=pyodrx.ContactPoint.end, sucRoad=roads[0], sucCP=cp1)
        
            
        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)

        # Last step, link connection series by curves

        self.createInternalConnectionsForConnectionSeres(roads, connectionSeres, junction)

        odr.updateRoads(roads)
        odr.resetAndReadjust(byPredecessor=True)

        return odr
        


    def createConnectionRoads(self, roads, adjusted=False, areaType = JunctionAreaTypes.SQUARE):


        if adjusted is False:
            # set up x,y positions and headings for the roads around the boundary of the area

            if areaType == JunctionAreaTypes.SQUARE:
                # maximum roads to connect to a side
                maxRoadsPerSide = math.floor(len(roads) / 4) + 1


    
    def createWithRandomLaneConfigurations(self, numRoads=3):

        raise NotImplementedError()



                
                    

            
