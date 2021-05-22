from junctions.LaneSides import LaneSides
from junctions.RoadBuilder import RoadBuilder
from extensions.ExtendedRoad import ExtendedRoad
from junctions.ODRHelper import ODRHelper
from junctions.RoadLinker import RoadLinker
from junctions.LaneBuilder import LaneBuilder
import pyodrx, logging

class NetworkConnection:

    def __init__(self, intersection1, road1, cp1, intersection2, road2, cp2, laneSides) -> None:

        self.intersection1 = intersection1
        self.road1 = road1
        self.cp1 = cp1
        self.intersection2 = intersection2
        self.road2 = road2
        self.cp2 = cp2
        self.laneSides = laneSides

        pass


class IncidentConnection:

    def __init__(self, road1, cp1, road2, cp2, laneSides, connectionRoad) -> None:

        self.road1 = road1
        self.cp1 = cp1
        self.road2 = road2
        self.cp2 = cp2
        self.laneSides = laneSides
        self.connectionRoad = connectionRoad

        pass


class Network:

    """ Holds the connections and clusters """


    def __init__(self, placedIntersections, debug=True) -> None:

        self.roadBuilder = RoadBuilder()
        self.laneBuilder = LaneBuilder()
        self.placedIntersections = {} # map DI -> I
        self.connectionRoads = []

        self.connectionList = {} # intersection to list of intersections

        self.clusters = []
        self.intersectionClusterMap = {}


        for intersection in placedIntersections.values():
            self.connectionList[intersection] = {}
            newCluster = set([intersection])
            self.clusters.append(newCluster)
            self.intersectionClusterMap[intersection] = newCluster

        self.debug = debug
        self.name = "Network"
        pass



    def connect(self, connectionRoadId, intersection1, road1: ExtendedRoad, cp1, intersection2, road2: ExtendedRoad, cp2, laneSides):


        if self.debug:
            logging.info(f"{self.name}: connecting intersections ({intersection1.id}, {intersection2.id})")


        connectionRoad = self.roadBuilder.getConnectionRoadBetween(connectionRoadId, road1, road2, cp1, cp2, isJunction=False, laneSides=laneSides)
        RoadLinker.createExtendedPredSuc(predRoad=road1, predCp=cp1, sucRoad=connectionRoad, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=connectionRoad, predCp=pyodrx.ContactPoint.end, sucRoad=road2, sucCP=cp2)

        self.laneBuilder.createLanesForConnectionRoad(connectionRoad, road1, road2)

        x, y, h = road1.getPosition(cp1)
        ODRHelper.transformRoad(connectionRoad, x, y, h)
        connectionRoad.planview.adjust_geometires()

        # x2, y2, h2 = road2.getPosition(cp2)
        # print(x, y, h)
        # print(x2, y2, h2)
        


        self.connectionList[intersection1][intersection2] = IncidentConnection(road1, cp1, road2, cp2, laneSides, connectionRoad)
        self.connectionList[intersection2][intersection1] = IncidentConnection(road2, cp2, road1, cp1, laneSides, connectionRoad)

        self.connectionRoads.append(connectionRoad)

        # set connection road's starting position

        self.addToTheSameCluster([intersection1, intersection2])

    
    def addToTheSameCluster(self, intersectionList):

        toCluster = None
        for intersection in intersectionList:
            if intersection in self.intersectionClusterMap:
                toCluster = self.intersectionClusterMap[intersection]
                break

        # some elements may be in another cluster. We need to import from those
        if toCluster is None: # create new cluster
            if self.debug:
                logging.info(f"{self.name}: creating new cluster")
            toCluster = set()
            self.clusters.append(toCluster)

        for intersection in intersectionList:
            if intersection in self.intersectionClusterMap:
                prevCluster = self.intersectionClusterMap[intersection]
                if self.debug:
                    logging.info(f"{self.name}: intersection {intersection.id} previously belongs  to ({self.getClusterString(toCluster)})")
                if prevCluster != toCluster:
                    self.importIntoCluster(toCluster, prevCluster)
            else:
                toCluster.add(intersection)
                self.intersectionClusterMap[intersection] = toCluster


    def importIntoCluster(self, toCluster, fromCluster):
        if self.debug:
            logging.info(f"{self.name}: mergeing clusters ({self.getClusterString(toCluster)}), ({self.getClusterString(fromCluster)})")
        for intersection in fromCluster:
            toCluster.add(intersection)
            self.intersectionClusterMap[intersection] = toCluster
        fromCluster.clear()
        self.clusters.remove(fromCluster)


    def logClusters(self):
        index = 0
        for cluster in self.clusters:
            cStr = self.getClusterString(cluster)
            logging.info(f"{self.name}: cluster {index}: {cStr}")
            index += 1

    def getClusterString(self, cluster):
        clusterIntersectionIds = [str(intersection.id) for intersection in cluster]
        return ",".join(clusterIntersectionIds)
                    




        