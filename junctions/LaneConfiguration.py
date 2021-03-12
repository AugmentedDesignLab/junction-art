from abc import ABC
from enum import Enum
import numpy as np
from extensions.ExtendedRoad import ExtendedRoad
from extensions.ExtendedLaneSection import ExtendedLaneSection
from library.Configuration import Configuration
from extensions.CountryCodes import CountryCodes
import pyodrx

class LaneConfigurationStrategies(Enum):
    MERGE_MEDIAN = "MERGE_MEDIAN"
    MERGE_EDGE = "MERGE_EDGE"
    MERGE_MID = "MERGE_MID"
    MERGE_DISTANCE = "MERGE_DISTANCE"
    NO_MERGE = "NO_MERGE"
    SPLIT_LAST = "SPLIT_LAST"
    SPLIT_FIRST = "SPLIT_FIRST"
    SPLIT_MULTI = "SPLIT_MULTI"
    SPLIT_ANY = "SPLIT_ANY"

    @staticmethod
    def getAvailableSplitStrategies():
        return [
            LaneConfigurationStrategies.SPLIT_FIRST,
            LaneConfigurationStrategies.SPLIT_LAST
        ]
    
    @staticmethod
    def getRandomAvailableSplitStrategy():
        strategies = LaneConfigurationStrategies.getAvailableSplitStrategies()
        return strategies[np.random.choice(len(strategies))]


class LaneConfiguration(ABC):

    @staticmethod
    def getNumberDifferentLanes(connections):
        numStandard = 0
        numMerge = 0
        numTurn = 0

        for i, j, conType in connections:
            if conType == 0:
                numStandard += 1
            elif conType == 1:
                numMerge += 1
            else:
                numTurn += 1

        return numStandard, numMerge, numTurn



    @staticmethod
    def getLaneLinks(laneSection1: ExtendedLaneSection, laneSection2: ExtendedLaneSection, isCpSame: bool, strategy = LaneConfigurationStrategies.MERGE_EDGE):

        if strategy == LaneConfigurationStrategies.MERGE_EDGE:
            return LaneConfiguration.getLaneLinksByMergingEdge(laneSection1, laneSection2, isCpSame)
        
        raise Exception(f"{strategy} not implemented")


    # methods for lane link configurations in an intersection

    @staticmethod
    def getIncomingLanesOnARoad(road, cp, countryCode):

        laneSection = road.getLaneSectionByCP(cp)
        if countryCode == CountryCodes.US:
            if cp == pyodrx.ContactPoint.start:
                return laneSection.leftlanes
            return laneSection.rightlanes
        
        raise NotImplementedError()

    @staticmethod
    def getIncomingLaneIdsOnARoad(road, cp, countryCode):
        return LaneConfiguration.getUniqueLaneIds(road, LaneConfiguration.getIncomingLanesOnARoad(road, cp, countryCode))

    @staticmethod
    def getOutgoingLanesOnARoad(road, cp, countryCode):

        laneSection = road.getLaneSectionByCP(cp)
        if countryCode == CountryCodes.US:
            if cp == pyodrx.ContactPoint.end:
                return laneSection.leftlanes
            return laneSection.rightlanes
        
        raise NotImplementedError()

    
    @staticmethod
    def getIncomingLanesIdsToARoad(outgoingRoad, allRoads, cp1, countryCode):
        """Assumes all roads are connected by start point except for the first one
           all the incoming lanes that enters the outgoingRoad

        Args:
            outgoingRoad ([type]): [description]
            allRoads ([type]): [description]
            cp1 ([type]): Contact point of the first road.
            countryCode ([type]): [description]
        """

        # allRoads may have the incoming road, too.
        outgoingLanes = []

        firstRoadId = allRoads[0].id

        if countryCode == CountryCodes.US:
            for road in allRoads:
                if road.id != outgoingRoad.id:
                    lanes = []
                    if road.id == firstRoadId:
                        lanes = LaneConfiguration.getIncomingLanesOnARoad(road, cp1, countryCode)
                    else:
                        lanes = LaneConfiguration.getIncomingLanesOnARoad(road, pyodrx.ContactPoint.start, countryCode)
                    
                    outgoingLanes += LaneConfiguration.getUniqueLaneIds(road, lanes)

            return outgoingLanes

        raise NotImplementedError()


    @staticmethod
    def getOutgoingLanesIdsFromARoad(incomingRoad, allRoads, cp1, countryCode):
        """Assumes all roads are connected by start point except for the first one
        all the outgoing lanes from the incoming road

        Args:
            incomingRoad ([type]): [description]
            allRoads ([type]): [description]
            cp1 ([type]): Contact point of the first road.
            countryCode ([type]): [description]
        """

        # allRoads may have the incoming road, too.
        outgoingLanes = []

        firstRoadId = allRoads[0].id

        if countryCode == CountryCodes.US:
            for road in allRoads:
                if road.id != incomingRoad.id:
                    lanes = []
                    if road.id == firstRoadId:
                        lanes = LaneConfiguration.getOutgoingLanesOnARoad(road, cp1, countryCode)
                    else:
                        lanes = LaneConfiguration.getOutgoingLanesOnARoad(road, pyodrx.ContactPoint.start, countryCode)
                    
                    outgoingLanes += LaneConfiguration.getUniqueLaneIds(road, lanes)

            return outgoingLanes

        raise NotImplementedError()



    @staticmethod
    def getUniqueLaneId(roadId, lane_id):

        return f"{roadId}:{lane_id}"



    @staticmethod
    def getUniqueLaneIds(road, lanes):

        roadId = road.id
        laneIds = []
        for lane in lanes:
            laneIds.append(LaneConfiguration.getUniqueLaneId(roadId, lane.lane_id))
        
        return laneIds







    @staticmethod
    def getIntersectionLinks1ToMany(incomingLanes, outgoingLanes, strategy=LaneConfigurationStrategies.SPLIT_ANY):
        """[summary]

        Args:
            incomingLanes ([type]): list of unique lane ids (1-2) means road 1, lane 2
            outgoingLanes ([type]): list of unique lane ids (1-2) means road 1, lane 2

        Returns:
            [type]: a list of left lane links and a list of right lane links. A lane link is a tuple (unique left lane id, unique right lane id, 0/1/2) 0 means = straight, 2 = split
        """
        if len(incomingLanes) > len(outgoingLanes):
            raise Exception("# of incoming lanes is greater than # of outgoing lanes in this intersection")

        if strategy == LaneConfigurationStrategies.SPLIT_ANY:
            strategy = LaneConfigurationStrategies.getRandomAvailableSplitStrategy()

        if strategy == LaneConfigurationStrategies.SPLIT_LAST:
            return LaneConfiguration.getIntersectionLinks1ToManyBySplittingLast(incomingLanes, outgoingLanes)
        if strategy == LaneConfigurationStrategies.SPLIT_FIRST:
            return LaneConfiguration.getIntersectionLinks1ToManyBySplittingFirst(incomingLanes, outgoingLanes)

        
    @staticmethod
    def getIntersectionLinks1ToManyBySplittingFirst(incomingLanes, outgoingLanes):
        """[summary]

        Args:
            incomingLanes ([type]): [description]
            outgoingLanes ([type]): [description]

        Returns:
            [type]: [description]
        """
        LaneConfiguration.validateIncomingAndOutgoingLanes(incomingLanes, outgoingLanes)

        if len(incomingLanes) == 0 or len(outgoingLanes) == 0:
            return []

        connections = LaneConfiguration.get1To1Connections(incomingLanes, outgoingLanes, fromTop=False)

        # now we have outgoing lanes on the top of the stack. We find the bottommost non-connected lane
        numNonConnectedOutgoing = len(outgoingLanes) - len(connections)

        if numNonConnectedOutgoing < 1:
            return connections

        lastNonConnectedIndex = numNonConnectedOutgoing - 1
            
        # split the last
        for i in range(numNonConnectedOutgoing):
            connections.insert(0, (incomingLanes[0], outgoingLanes[lastNonConnectedIndex - i], 2))

        return connections

        
    @staticmethod
    def getIntersectionLinks1ToManyBySplittingLast(incomingLanes, outgoingLanes):
        """[summary]

        Args:
            incomingLanes ([type]): [description]
            outgoingLanes ([type]): [description]

        Returns:
            [type]: [description]
        """
        LaneConfiguration.validateIncomingAndOutgoingLanes(incomingLanes, outgoingLanes)

        if len(incomingLanes) == 0 or len(outgoingLanes) == 0:
            return []

        connections = LaneConfiguration.get1To1Connections(incomingLanes, outgoingLanes)
            
        # split the last
        for i in range(len(outgoingLanes) - len(incomingLanes)):
            connections.append((incomingLanes[-1], outgoingLanes[i + len(incomingLanes)], 2))

        return connections

    @staticmethod
    def get1To1Connections(incomingLanes, outgoingLanes, fromTop=True):
        connections = []
        if fromTop:
            for i in range(len(incomingLanes)):
                connections.append((incomingLanes[i], outgoingLanes[i], 0))
        else:
            # we start at the bottom of two stacks and insert connections at the top.
            incomingLastIndex = len(incomingLanes) - 1
            outgoingLastIndex = len(outgoingLanes) - 1
            for i in range(len(incomingLanes)):
                connections.insert(0, (incomingLanes[incomingLastIndex - i], outgoingLanes[outgoingLastIndex - i], 0))

        return connections

    @staticmethod
    def validateIncomingAndOutgoingLanes(incomingLanes, outgoingLanes):
        if len(incomingLanes) > len(outgoingLanes):
            raise Exception("Splitting last will not work if # of incoming lanes is >= # of outgoing lanes in this intersection ")




    @staticmethod
    def getLaneLinksByMergingEdge(laneSection1: ExtendedLaneSection, laneSection2: ExtendedLaneSection, isCpSame: bool):
        """[summary]

        Args:
            laneSection1 (ExtendedLaneSection): [description]
            laneSection2 (ExtendedLaneSection): [description]
        Returns:
            a list of left lane links and a list of right lane links. A lane link is a tuple (laneId on road1, laneId on road2, 0/1/2) 0 means = straight, 1 = merge, 2 = turn
        """
        sign = 1
        if isCpSame:
            sign = -1 # left lanes with right

        leftConnections = []
        rightConnections = []

        # left lanes
        lanes1 = laneSection1.leftlanes
        lanes2 = laneSection2.leftlanes
        if isCpSame:
            lanes2 = laneSection2.rightlanes

        nonMergeIds = min(len(lanes1), len(lanes2))
        if nonMergeIds > 0:
            curId = 1
            for _ in range(nonMergeIds): # commons
                leftConnections.append((curId, curId * sign, 0))
                curId += 1
            
            if len(lanes1) > len(lanes2):  # merges on the first

                edgeId2 = lanes2[-1].lane_id
                diff = len(lanes1) - len(lanes2)
                for _ in range(diff):
                    leftConnections.append((curId, edgeId2, 1))
                    curId += 1
            elif len(lanes1) < len(lanes2): # merges on the second
                edgeId1 = lanes1[-1].lane_id
                diff = len(lanes2) - len(lanes1)
                for _ in range(diff):
                    leftConnections.append((edgeId1, curId * sign, 2))
                    curId += 1

        
        
        # right lanes
        lanes1 = laneSection1.rightlanes
        lanes2 = laneSection2.rightlanes

        if isCpSame:
            lanes2 = laneSection2.leftlanes

        nonMergeIds = min(len(lanes1), len(lanes2))
        if nonMergeIds > 0:
            curId = -1
            for _ in range(nonMergeIds):
                rightConnections.append((curId, curId * sign, 0))
                curId -= 1
            
            if len(lanes1) > len(lanes2):
                edgeId2 = lanes2[-1].lane_id
                diff = len(lanes1) - len(lanes2)
                for _ in range(diff):
                    rightConnections.append((curId, edgeId2, 1))
                    curId -= 1

            elif len(lanes1) < len(lanes2): # merges on the second
                edgeId1 = lanes1[-1].lane_id
                diff = len(lanes2) - len(lanes1)
                for _ in range(diff):
                    rightConnections.append((edgeId1, curId * sign, 2))
                    curId -= 1


        return leftConnections, rightConnections






