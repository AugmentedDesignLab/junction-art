from enum import Enum
import numpy as np


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
