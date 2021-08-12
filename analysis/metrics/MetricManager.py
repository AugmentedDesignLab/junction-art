from junctions.Intersection import Intersection
from analysis.metrics.travel.ConnectionRoadComplexity import ConnectionRoadComplexity
from typing import List
import pandas as pd

class MetricManager:

    def __init__(self, intersections: List[Intersection], metricConfigs = None) -> None:
        self.intersections = intersections
        self.metricConfigs = metricConfigs
        self.connectionRoadDF = pd.DataFrame()
        self.incidentRoadDF = pd.DataFrame()
        self.calculateCoreStatistics()
        pass


    def getNormalizedTurnComplexities(self):
        
        minPathLengthIntersection = 10
        if (self.metricConfigs is not None) and ("minPathLengthIntersection" in self.metricConfigs):
            minPathLengthIntersection = self.metricConfigs["minPathLengthIntersection"]

        complexities = []
        for intersection in self.intersections:
            connectionRoadComplexity = ConnectionRoadComplexity(intersection, minPathLengthIntersection=minPathLengthIntersection)
            complexities.append(connectionRoadComplexity.getMaxTurnComplexity())
        
        self.connectionRoadDF["turnComplexities"] = complexities
        return complexities

    
    def calculateCoreStatistics(self):
        minPathLengthIntersection = 10
        numberOfLanes = []
        numberOfIncidentRoads = []
        numberOfConnectionRoads = []
        numberOfIncomingLanes = []
        complexities = []
        intersectionIds = []

        for intersection in self.intersections:
            intersectionIds.append(intersection.id)
            numberOfIncidentRoads.append(len(intersection.incidentRoads))
            numberOfConnectionRoads.append(len(intersection.internalConnectionRoads))
            connectionRoadComplexity = ConnectionRoadComplexity(intersection, minPathLengthIntersection=minPathLengthIntersection)
            complexities.append(connectionRoadComplexity.getMaxTurnComplexity())
        
        self.connectionRoadDF["numberOfIncidentRoads"] = pd.Series(numberOfIncidentRoads)
        self.connectionRoadDF["numberOfConnectionRoads"] = pd.Series(numberOfConnectionRoads)
        self.connectionRoadDF["id"] = pd.Series(intersectionIds)
        pass