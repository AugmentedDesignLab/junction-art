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
    def getLaneLinks(laneSection1: ExtendedLaneSection, laneSection2: ExtendedLaneSection, strategy = LaneConfigurationStrategies.MERGE_EDGE):

        if strategy == LaneConfigurationStrategies.MERGE_EDGE:
            return LaneConfiguration.getLaneLinksByMergingEdge(laneSection1, laneSection2)
        
        raise Exception(f"{strategy} not implemented")


    @staticmethod
    def getLaneLinksByMergingEdge(laneSection1: ExtendedLaneSection, laneSection2: ExtendedLaneSection):
        """[summary]

        Args:
            laneSection1 (ExtendedLaneSection): [description]
            laneSection2 (ExtendedLaneSection): [description]
        Returns:
            a list of left lane links and a list of right lane links. A lane link is a tuple (laneId on road1, laneId on road2, isMerge)
        """

        leftConnections = []
        rightConnections = []

        # left lanes
        lanes1 = laneSection1.leftlanes
        lanes2 = laneSection2.leftlanes

        nonMergeIds = min(len(lanes1), len(lanes2))
        if nonMergeIds > 0:
            curId = 1
            for _ in range(nonMergeIds): # commons
                leftConnections.append((curId, curId, False))
                curId += 1
            
            if len(lanes1) > len(lanes2):  # merges on the first

                edgeId2 = lanes2[-1].lane_id
                diff = len(lanes1) - len(lanes2)
                for _ in range(diff):
                    leftConnections.append((curId, edgeId2, True))
                    curId += 1
            elif len(lanes1) < len(lanes2): # merges on the second
                edgeId1 = lanes1[-1].lane_id
                diff = len(lanes2) - len(lanes1)
                for _ in range(diff):
                    leftConnections.append((edgeId1, curId, True))
                    curId += 1

        
        
        # right lanes
        lanes1 = laneSection1.rightlanes
        lanes2 = laneSection2.rightlanes

        nonMergeIds = min(len(lanes1), len(lanes2))
        if nonMergeIds > 0:
            curId = -1
            for _ in range(nonMergeIds):
                rightConnections.append((curId, curId, False))
                curId -= 1
            
            if len(lanes1) > len(lanes2):
                edgeId2 = lanes2[-1].lane_id
                diff = len(lanes1) - len(lanes2)
                for _ in range(diff):
                    rightConnections.append((curId, edgeId2, True))
                    curId -= 1

            elif len(lanes1) < len(lanes2): # merges on the second
                edgeId1 = lanes1[-1].lane_id
                diff = len(lanes2) - len(lanes1)
                for _ in range(diff):
                    rightConnections.append((edgeId1, curId, True))
                    curId -= 1


        return leftConnections, rightConnections






