from junctionart.junctions.Intersection import Intersection
from junctionart.junctions.Geometry import Geometry
from junctionart.extensions.ExtendedRoad import ExtendedRoad
import junctionart.extensions
import math
from analysis.metrics.fov.Angle import Angle
from analysis.metrics.fov.Fov import Fov
from analysis.metrics.fov.FovComplexity import FovComplexity
import pandas as pd
import numpy as np

class IncidentRoadComplexity:

    def __init__(self, intersection: Intersection, minPathLengthIntersection=10) -> None:
        self.intersection = intersection
        self.minPathLengthIntersection = minPathLengthIntersection
        self.name = f"IncidentRoadComplexity #{self.intersection.id}"
        self.incidentRoadCharacteristics = {}
        self.incidentRoadDf = None
        self.initIncidentRoadCharacteristics()
        self.minCornerAngle = None
        self.maxDeviationAngle = None
        self.maxCurvature = None
        self.minDistance = None
        self.maxFov = None
        self.calculateStatistics()

    
    def initIncidentRoadCharacteristics(self):

        for incidentRoad in self.intersection.incidentRoads:
            self.incidentRoadCharacteristics[incidentRoad] = {
                'fov' : None,
                'corner' : None,
                'cornerDeviation' : None,
                'fovComplexity' : None
            }
        pass

    

    def getMinCornerAngle(self):
        if self.minCornerAngle is None:
            self.calculateStatistics()
        return self.minCornerAngle


    def calculateStatistics(self):

        rows = []
        
        for incidentCP, incidentRoad in zip(self.intersection.incidentCPs, self.intersection.incidentRoads):

            otherCP = extensions.reverseCP(incidentCP)
            p0x, p0y, _ = incidentRoad.getPosition(otherCP)
            p1x, p1y, h1 = incidentRoad.getPosition(incidentCP)
            p0 = (p0x, p0y)
            p1 = (p1x, p1y)
            # cornerAngle, deviationAngle = self.measureMinCornerAndDeviationFrom(incidentRoad, p0, p1)
            roadStats = self.getRoadStats(incidentRoad, p0, p1, h1)
            fov = Fov.getFovFromMinCorner(roadStats['cornerAngle'])

            self.incidentRoadCharacteristics[incidentRoad]['corner'] = math.degrees(roadStats['cornerAngle'])
            self.incidentRoadCharacteristics[incidentRoad]['cornerDeviation'] = math.degrees(roadStats['deviationAngle'])
            self.incidentRoadCharacteristics[incidentRoad]['fov'] = math.degrees(fov)
            complexity = self.getComplexity(curvature=roadStats['maxCurvature'], fov=fov, deviationFromfov=roadStats['deviationAngle'])
            complexity_avg = self.getComplexityAvg(curvature=roadStats['maxCurvature'], fov=fov, deviationFromfov=roadStats['deviationAngle'])
            complexity_max = self.getComplexityMax(curvature=roadStats['maxCurvature'], fov=fov, deviationFromfov=roadStats['deviationAngle'])

            rows.append({
                
                'fov' : math.degrees(fov),
                'fovNorm' : self.getNormFov(fov),
                'corner' : math.degrees(roadStats['cornerAngle']),
                'cornerDeviation' : math.degrees(roadStats['deviationAngle']),
                'cornerDeviationNorm' : self.getNormDeviation(roadStats['deviationAngle']),
                'minDistance' : roadStats['minDistance'],
                'maxCurvature' : math.degrees(roadStats['maxCurvature']),
                'maxCurvatureNorm': self.getNormCurvature(roadStats['maxCurvature']),
                'complexity' : complexity,
                'complexity_avg' : complexity_avg,
                'complexity_max' : complexity_max,
            })

            # intersection summary
            if (self.maxFov is None) or (self.maxFov < fov):
                self.maxFov = fov

            if (self.minCornerAngle is None) or (roadStats['cornerAngle'] < self.minCornerAngle):
                self.minCornerAngle = roadStats['cornerAngle']
            
            if (self.maxDeviationAngle is None) or (self.maxDeviationAngle < roadStats['deviationAngle']):
                self.maxDeviationAngle = roadStats['deviationAngle']
            
            pass
        
        self.incidentRoadDf = pd.DataFrame(rows)
        pass

    
    
    def getRoadStats(self, fromRoad: ExtendedRoad, p0, p1, h1):

        minAngle = 3.15
        maxDeviation = 0
        minDistance = None
        maxCurvature = 0
        for incidentCP, incidentRoad in zip(self.intersection.incidentCPs, self.intersection.incidentRoads):
            if incidentRoad == fromRoad:
                continue

            otherCP = extensions.reverseCP(incidentCP)
            p2x, p2y, h2 = incidentRoad.getPosition(incidentCP)
            p3x, p3y, _ = incidentRoad.getPosition(otherCP)
            p2 = (p2x, p2y)
            p3 = (p3x, p3y)
            angle = Angle.cornerAngle(p0, p1, p2)
            deviationAngle = FovComplexity.getAngleDeviationFromSightLine(p1, p2, p3)
            distance = self.getLinearDistance(p1, p2)
            curvature = self.getAvgCurvature(h1, h2, distance)

            # print(f"{self.name}: p0 = ({p0}), p1 = ({p1}), p2 = ({p2}), p2 = ({p3})")
            # print(f"{self.name}: Corner angle between road {fromRoad.id} and {incidentRoad.id} is {math.degrees(angle)}. Deviation is {math.degrees(deviationAngle)}")
            # print(f"{self.name}: distance between road {fromRoad.id} and {incidentRoad.id} is {distance}. curvature is {math.degrees(curvature)}")

            if angle < minAngle:
                minAngle = angle
            if maxDeviation < deviationAngle:
                maxDeviation = deviationAngle

            if (minDistance is None) or (minDistance > distance):
                minDistance = distance
            
            if maxCurvature < curvature:
                maxCurvature = curvature

        
        return {
            'cornerAngle': minAngle,
            'deviationAngle': maxDeviation,
            'minDistance': minDistance,
            'maxCurvature': maxCurvature

        }


    def getMaxCurvature(self):
        return (np.pi * 2) / self.minPathLengthIntersection # curvature of a Uturn
    
    def getNormCurvature(self, curvature):
        return curvature / self.getMaxCurvature()

    def getNormDeviation(self, deviationFromfov):
        return deviationFromfov / (np.pi / 2) #assuming max is 90

    def getNormFov(self, fov):
        return fov / (np.pi * 1.1) # assuming max is 180


    def getComplexity(self, curvature, fov, deviationFromfov):
        norm_curvature = self.getNormCurvature(curvature)
        normFov = self.getNormFov(fov)
        normDeviation = self.getNormDeviation(deviationFromfov)
        complexity = norm_curvature * normFov * normDeviation

        if complexity > 1:
            print(f"{self.name}:getComplexity  complexity over 1. curvature={curvature}, maxCurvature={self.getMaxCurvature()},  norm_curvature={norm_curvature}, normFov={normFov}, normDeviation={normDeviation}")
            complexity = 1.0
        return complexity

    def getComplexityAvg(self, curvature, fov, deviationFromfov):
        norm_curvature = self.getNormCurvature(curvature)
        normFov = self.getNormFov(fov)
        normDeviation = self.getNormDeviation(deviationFromfov)
        complexity = 0.5 * norm_curvature + 0.25 * (normFov + normDeviation)

        if complexity > 1:
            print(f"{self.name}:getComplexity  complexity over 1. curvature={curvature}, maxCurvature={self.getMaxCurvature()},  norm_curvature={norm_curvature}, normFov={normFov}, normDeviation={normDeviation}")
            complexity = 1.0
        return complexity


    def getComplexityMax(self, curvature, fov, deviationFromfov):
        norm_curvature = self.getNormCurvature(curvature)
        normFov = self.getNormFov(fov)
        normDeviation = self.getNormDeviation(deviationFromfov)
        complexity = max(norm_curvature, normFov, normDeviation)

        if complexity > 1:
            print(f"{self.name}:getComplexity  complexity over 1. curvature={curvature}, maxCurvature={self.getMaxCurvature()},  norm_curvature={norm_curvature}, normFov={normFov}, normDeviation={normDeviation}")
            complexity = 1.0
        return complexity


    def getLinearDistance(self, p1, p2):
        return math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))


    
    def getAvgCurvature(self, h1, h2, distance):
        h1 = Geometry.positiveNormalizeHeading(h1)
        h2 = Geometry.positiveNormalizeHeading(h2)
        # print(h1, h2, distance)
        return round(abs(h1 - h2) / distance, 2)
