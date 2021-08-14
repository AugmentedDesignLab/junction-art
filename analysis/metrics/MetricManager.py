from analysis.metrics.fov.IncidentRoadComplexity import IncidentRoadComplexity
from junctions.Intersection import Intersection
from analysis.metrics.travel.ConnectionRoadComplexity import ConnectionRoadComplexity
from typing import List
import pandas as pd
from datetime import datetime

class MetricManager:

    def __init__(self, intersections: List[Intersection], metricConfigs = None) -> None:
        self.name = "MetricManager"
        self.intersections = intersections
        self.metricConfigs = metricConfigs
        self.connectionRoadDF = pd.DataFrame()
        self.incidentRoadDF = pd.DataFrame()
        self.intersectionDF = pd.DataFrame()
        self.calculateIntersectionStatistics()
        pass
    

    def getMinConnectionPath(self):
        
        minPathLengthIntersection = 10
        if (self.metricConfigs is not None) and ("minPathLengthIntersection" in self.metricConfigs):
            minPathLengthIntersection = self.metricConfigs["minPathLengthIntersection"]
        return minPathLengthIntersection

    def getNormalizedTurnComplexities(self):
        
        minPathLengthIntersection = self.getMinConnectionPath()

        complexities = []
        for intersection in self.intersections:
            connectionRoadComplexity = ConnectionRoadComplexity(intersection, minPathLengthIntersection=minPathLengthIntersection)
            complexities.append(connectionRoadComplexity.getMaxTurnComplexity())
        
        self.intersectionDF["turnComplexities"] = complexities
        return complexities

    
    def calculateIntersectionStatistics(self):
        numberOfIncidentRoads = []
        numberOfConnectionRoads = []
        intersectionIds = []

        for intersection in self.intersections:
            intersectionIds.append(intersection.id)
            numberOfIncidentRoads.append(len(intersection.incidentRoads))
            numberOfConnectionRoads.append(len(intersection.internalConnectionRoads))
            # connectionRoadComplexity = ConnectionRoadComplexity(intersection, minPathLengthIntersection=minPathLengthIntersection)

            print(f"{self.name}: calculateIntersectionStatistics done for intersection {intersection.id}")
        
        self.intersectionDF["numberOfIncidentRoads"] = pd.Series(numberOfIncidentRoads)
        self.intersectionDF["numberOfConnectionRoads"] = pd.Series(numberOfConnectionRoads)
        self.intersectionDF["id"] = pd.Series(intersectionIds)

        
        self.calculateConnectionRoadStatistics()
        self.calculateIncidentRoadStatistics()
        pass

    
    def calculateConnectionRoadStatistics(self):
        
        minPathLengthIntersection = self.getMinConnectionPath()

        frames = []
        for intersection in self.intersections:
            connectionRoadComplexity = ConnectionRoadComplexity(intersection, minPathLengthIntersection=minPathLengthIntersection)
            connectionRoadComplexity.connectRoadDf['intersectionId'] = intersection.id
            frames.append(connectionRoadComplexity.connectRoadDf)
        
        self.connectionRoadDF = pd.concat(frames, ignore_index=True)


    def calculateIncidentRoadStatistics(self):

        minPathLengthIntersection = self.getMinConnectionPath()
        
        frames = []
        for intersection in self.intersections:
            incidentRoadComplexity = IncidentRoadComplexity(intersection, minPathLengthIntersection=minPathLengthIntersection)
            incidentRoadComplexity.incidentRoadDf['intersectionId'] = intersection.id
            frames.append(incidentRoadComplexity.incidentRoadDf)
            print(f"{self.name}: calculateIncidentRoadStatistics done for intersection {intersection.id}")
        
        self.incidentRoadDF = pd.concat(frames, ignore_index=True)

    

    def exportDataframes(self, path):
        
        suf = datetime.now().strftime("%Y-%m-%d")
        incidentPath = f"{path}/{suf}-incidentRoadDF.csv"
        connectionPath = f"{path}/{suf}-connectionRoadDF.csv"
        intersectionPath = f"{path}/{suf}-intersectionDF.csv"

        print(incidentPath)
        print(connectionPath)
        print(intersectionPath)

        self.incidentRoadDF.to_csv(incidentPath, index=False)
        self.connectionRoadDF.to_csv(connectionPath, index=False)
        self.intersectionDF.to_csv(intersectionPath, index=False)

    
    

        
