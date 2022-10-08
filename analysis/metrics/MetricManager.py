import logging, os
import junctionart.extensions as extensions
from junctionart.library.Configuration import Configuration
from analysis.metrics.fov.IncidentRoadComplexity import IncidentRoadComplexity
from junctionart.junctions.Intersection import Intersection
from analysis.metrics.travel.ConnectionRoadComplexity import ConnectionRoadComplexity
from typing import List
import pandas as pd
from datetime import datetime

from junctionart.draw.IntersectionDrawer import IntersectionDrawer
import numpy as np

class MetricManager:

    def __init__(self, intersections: List[Intersection], metricConfigs = None, startStats=True) -> None:
        self.configuration = Configuration()
        self.name = "MetricManager"
        self.intersections = intersections
        self.metricConfigs = metricConfigs
        self.connectionRoadDF = pd.DataFrame()
        self.incidentRoadDF = pd.DataFrame()
        self.intersectionDF = pd.DataFrame()
        if startStats:
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
        areas = []
        conflictAreas = []
        intersectionCount = 0
        for intersection in self.intersections:

            if len(intersection.incidentRoads) < 3:
                raise Exception("Metrics available for 3+ leg intersections only")

            try:
                numberOfIncidentRoads.append(len(intersection.incidentRoads))
                numberOfConnectionRoads.append(len(intersection.internalConnectionRoads))

                area_dict = IntersectionDrawer(intersection, step=0.1).get_area_values(include_u_turn=False)
                areas.append(area_dict['IntersectionArea'])
                conflictAreas.append(area_dict['ConflictArea'])
                
                intersectionCount += 1
                intersectionIds.append(intersectionCount)

                

                logging.debug(f"{self.name}: calculateIntersectionStatistics done for intersection {intersectionCount}")
            except Exception as e:
                extensions.view_road(intersection.odr,os.path.join('..',self.configuration.get("esminipath")))
                logging.error(e)
                raise e

        
        self.intersectionDF["numberOfIncidentRoads"] = pd.Series(numberOfIncidentRoads)
        self.intersectionDF["numberOfConnectionRoads"] = pd.Series(numberOfConnectionRoads)
        self.intersectionDF["id"] = pd.Series(intersectionIds)
        # print(self.intersectionDF.columns)
        self.intersectionDF.set_index([intersectionIds], inplace=True)

        self.intersectionDF['area'] = pd.Series(areas)
        self.intersectionDF['conflictArea'] = pd.Series(conflictAreas)
        # self.intersectionDF['conflictPoints'] = None
        # self.

        
        self.calculateConnectionRoadStatistics()
        self.calculateIncidentRoadStatistics()

        self.intersectionDF = self.addExtraSummaryForIntersections(self.intersectionDF, self.incidentRoadDF, self.connectionRoadDF)
        pass

    
    def calculateConnectionRoadStatistics(self):
        
        minPathLengthIntersection = self.getMinConnectionPath()

        frames = []
        intersectionCount = 0
        for intersection in self.intersections:
            try:
                connectionRoadComplexity = ConnectionRoadComplexity(intersection, minPathLengthIntersection=minPathLengthIntersection)
                connectionRoadComplexity.connectRoadDf['legs'] = len(intersection.incidentRoads)
        

                if connectionRoadComplexity.connectRoadDf['turnCurvature'].max() > 45:
                    self.viewIntersection(intersection)
                
                
                intersectionCount += 1
                connectionRoadComplexity.connectRoadDf['intersectionId'] = intersectionCount
                frames.append(connectionRoadComplexity.connectRoadDf)

                logging.debug(f"{self.name}: calculateConnectionRoadStatistics done for intersection {intersectionCount}")

            except Exception as e:
                logging.error(e)
                extensions.view_road(intersection.odr,os.path.join('..',self.configuration.get("esminipath")))
                raise e
            
        
        self.connectionRoadDF = pd.concat(frames, ignore_index=True)


    def calculateIncidentRoadStatistics(self):

        minPathLengthIntersection = self.getMinConnectionPath()
        
        frames = []
        intersectionCount = 0
        for intersection in self.intersections:
            try:
                incidentRoadComplexity = IncidentRoadComplexity(intersection, minPathLengthIntersection=minPathLengthIntersection)
                incidentRoadComplexity.incidentRoadDf['legs'] = len(intersection.incidentRoads)


                if incidentRoadComplexity.incidentRoadDf['maxCurvatureNorm'].max() > 2:
                    self.viewIntersection(intersection)

                intersectionCount += 1
                incidentRoadComplexity.incidentRoadDf['intersectionId'] = intersectionCount
                frames.append(incidentRoadComplexity.incidentRoadDf)

                logging.debug(f"{self.name}: calculateIncidentRoadStatistics done for intersection {intersectionCount}")

            except Exception as e:
                logging.error(e)
                extensions.view_road(intersection.odr,os.path.join('..',self.configuration.get("esminipath")))
                raise e
        
        self.incidentRoadDF = pd.concat(frames, ignore_index=True)

    
    def viewIntersection(self, intersection):
        extensions.view_road(intersection.odr,os.path.join('..',self.configuration.get("esminipath")))


    def exportDataframes(self, path):

        os.makedirs(path, exist_ok=True)
        
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


    def drawRandomIntersectionConflictAreas(self, n=5):

        for _ in range(n):
            i = np.random.randint(0, len(self.intersections))
            if len(self.intersections[i].incidentRoads) == 3:
                drawer = IntersectionDrawer(self.intersections[i], step=0.1)
                drawer.draw_intersection_and_conflict_area_fill()

    
    @staticmethod
    def addExtraSummaryForIntersections(intersectionDF:pd.DataFrame, incidentDF:pd.DataFrame, connectionDF:pd.DataFrame=None):

        # fov
        groupedIncidentDF = incidentDF.groupby(['intersectionId']).max()[['fov', 'maxCurvature', 'complexity_avg', 'cornerDeviation']]

        logging.info(groupedIncidentDF.head())
        # print(groupedIncidentDF.index)
        intersectionDF = intersectionDF.join(groupedIncidentDF, how='left')

        return intersectionDF
    
    

        
