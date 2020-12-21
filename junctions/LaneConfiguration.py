from abc import ABC
from enum import Enum
from extensions.ExtendedRoad import ExtendedRoad
from extensions.ExtendedLaneSection import ExtendedLaneSection

class LaneConfigurationStrategies(Enum):
    MERGE_MEDIAN = "MERGE_MEDIAN"
    MERGE_EDGE = "MERGE_EDGE"
    MERGE_MID = "MERGE_MID"
    MERGE_DISTANCE = "MERGE_DISTANCE"

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






