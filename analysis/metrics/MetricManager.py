import logging, os, extensions
from library.Configuration import Configuration
from analysis.metrics.fov.IncidentRoadComplexity import IncidentRoadComplexity
from junctions.Intersection import Intersection
from analysis.metrics.travel.ConnectionRoadComplexity import ConnectionRoadComplexity
from typing import List
import pandas as pd
from datetime import datetime

# from draw.IntersectionDrawer import IntersectionDrawer

class MetricManager:

    def __init__(self, intersections: List[Intersection], metricConfigs = None) -> None:
        self.configuration = Configuration()
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
        areas = []
        conflictAreas = []

        for intersection in self.intersections:

            if len(intersection.incidentRoads) < 3:
                raise Exception("Metrics available for 3+ leg intersections only")

            try:
                intersectionIds.append(intersection.id)
                numberOfIncidentRoads.append(len(intersection.incidentRoads))
                numberOfConnectionRoads.append(len(intersection.internalConnectionRoads))
                # connectionRoadComplexity = ConnectionRoadComplexity(intersection, minPathLengthIntersection=minPathLengthIntersection)

                # area_dict = IntersectionDrawer(intersection, step=0.1).get_area_values(include_u_turn=False)
                # areas.append(area_dict['IntersectionArea'])
                # conflictAreas.append(area_dict['ConflictArea'])

                

                print(f"{self.name}: calculateIntersectionStatistics done for intersection {intersection.id}")
            except Exception as e:
                extensions.view_road(intersection.odr,os.path.join('..',self.configuration.get("esminipath")))
                logging.error(e)
                raise e

        
        self.intersectionDF["numberOfIncidentRoads"] = pd.Series(numberOfIncidentRoads)
        self.intersectionDF["numberOfConnectionRoads"] = pd.Series(numberOfConnectionRoads)
        self.intersectionDF["id"] = pd.Series(intersectionIds)

        # self.intersectionDF['area'] = pd.Series(areas)
        # self.intersectionDF['conflictArea'] = pd.Series(conflictAreas)
        self.intersectionDF['conflictPoints'] = None
        # self.

        
        self.calculateConnectionRoadStatistics()
        self.calculateIncidentRoadStatistics()
        pass

    
    def calculateConnectionRoadStatistics(self):
        
        minPathLengthIntersection = self.getMinConnectionPath()

        frames = []
        for intersection in self.intersections:
            try:
                connectionRoadComplexity = ConnectionRoadComplexity(intersection, minPathLengthIntersection=minPathLengthIntersection)
                connectionRoadComplexity.connectRoadDf['intersectionId'] = intersection.id
                connectionRoadComplexity.connectRoadDf['legs'] = len(intersection.incidentRoads)
                frames.append(connectionRoadComplexity.connectRoadDf)
        
                logging.debug(f"{self.name}: calculateConnectionRoadStatistics done for intersection {intersection.id}")

                if connectionRoadComplexity.connectRoadDf['turnCurvature'].max() > 45:
                    self.viewIntersection(intersection)

            except Exception as e:
                logging.error(e)
                extensions.view_road(intersection.odr,os.path.join('..',self.configuration.get("esminipath")))
                raise e
            
        
        self.connectionRoadDF = pd.concat(frames, ignore_index=True)


    def calculateIncidentRoadStatistics(self):

        minPathLengthIntersection = self.getMinConnectionPath()
        
        frames = []
        for intersection in self.intersections:
            try:
                incidentRoadComplexity = IncidentRoadComplexity(intersection, minPathLengthIntersection=minPathLengthIntersection)
                incidentRoadComplexity.incidentRoadDf['intersectionId'] = intersection.id
                incidentRoadComplexity.incidentRoadDf['legs'] = len(intersection.incidentRoads)
                frames.append(incidentRoadComplexity.incidentRoadDf)

                logging.debug(f"{self.name}: calculateIncidentRoadStatistics done for intersection {intersection.id}")

                if incidentRoadComplexity.incidentRoadDf['maxCurvatureNorm'].max() > 2:
                    self.viewIntersection(intersection)

            except Exception as e:
                logging.error(e)
                extensions.view_road(intersection.odr,os.path.join('..',self.configuration.get("esminipath")))
                raise e
        
        self.incidentRoadDF = pd.concat(frames, ignore_index=True)

    
    def viewIntersection(self, intersection):
        extensions.view_road(intersection.odr,os.path.join('..',self.configuration.get("esminipath")))


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

    
    

        
