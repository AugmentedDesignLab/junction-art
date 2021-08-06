from junctions.Intersection import Intersection
from analysis.metrics.intersection_complexity.IntersectionComplexity import IntersectionComplexity
from typing import List
import pandas as pd

class MetricManager:

    def __init__(self, intersections: List[Intersection], metricConfigs = None) -> None:
        self.intersections = intersections
        self.metricConfigs = metricConfigs
        self.metricsDF = pd.DataFrame()
        self.calculateCoreStatistics()
        pass


    def getNormalizedTurnComplexities(self):
        
        minPathLengthIntersection = 10
        if (self.metricConfigs is not None) and ("minPathLengthIntersection" in self.metricConfigs):
            minPathLengthIntersection = self.metricConfigs["minPathLengthIntersection"]

        complexities = []
        for intersection in self.intersections:
            intersectionComplexity = IntersectionComplexity(intersection, minPathLengthIntersection=minPathLengthIntersection)
            complexities.append(intersectionComplexity.getMaxTurnComplexity())
        
        self.metricsDF["turnComplexities"] = complexities
        return complexities

    
    def calculateCoreStatistics(self):

        numberOfLanes = []
        numberOfIncidentRoads = []
        numberOfConnectionRoads = []
        numberOfIncomingLanes = []
        intersectionIds = []

        for intersection in self.intersections:
            intersectionIds.append(intersection.id)
            numberOfIncidentRoads.append(len(intersection.incidentRoads))
            numberOfConnectionRoads.append(len(intersection.internalConnectionRoads))
        
        self.metricsDF["numberOfIncidentRoads"] = pd.Series(numberOfIncidentRoads)
        self.metricsDF["numberOfConnectionRoads"] = pd.Series(numberOfConnectionRoads)
        self.metricsDF["id"] = pd.Series(intersectionIds)
        pass