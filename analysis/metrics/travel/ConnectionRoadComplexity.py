from numpy.core.arrayprint import printoptions
from junctions.Intersection import Intersection
from analysis.metrics.travel.TurnComplexity import TurnComplexity
from analysis.metrics.fov.IncidentRoadComplexity import IncidentRoadComplexity
from shapely.geometry import Polygon
import pandas as pd
import numpy as np

class ConnectionRoadComplexity:


    def __init__(self, intersection: Intersection, minPathLengthIntersection=10) -> None:
        self.intersection = intersection
        self.minPathLengthIntersection = minPathLengthIntersection
        # self.fovComplexity = IncidentRoadComplexity(intersection)
        self.connectRoadDf = None
        self.connectionRoadCharacteristics = {}
        self.initConnectionRoadCharacteristics()
        self.turnComplexities = {}
        self.measureTurnComplexities()
        self.area = self.measureArea()
        self.name = f"ConnectionRoadComplexity #{self.intersection.id}"
        pass


    def measureArea(self):
        
        try:
            vertices = []
            for incidentCP, incidentRoad in zip(self.intersection.incidentCPs, self.intersection.incidentRoads):
                x, y, _ = incidentRoad.getPosition(incidentCP)
                vertices.append((x, y))
            
            poly = Polygon(vertices)
            return poly.area
        except Exception as e:
            print(vertices)
            print(len(self.intersection.incidentRoads))
            raise e

    
    
    def initConnectionRoadCharacteristics(self):

        if self.intersection.internalConnectionRoads is None:
            raise Exception(f"{self.name}: missing internalConnectionRoads")

        for road in self.intersection.internalConnectionRoads:
            self.connectionRoadCharacteristics[road] = {
                'turnCurvature' : None,
                'turnCurvatureNorm' : None,
                'turnLength' : None
            }
        pass

    def printTurnComplexities(self):

        output = ""
        for connectionRoad in self.turnComplexities:
            output += f"\t{connectionRoad.id}: {self.turnComplexities[connectionRoad].__str__()}"
        print(output)

    def measureTurnComplexities(self):
        # find the left and right turn roads
        # measure complexities

        # We need to do it for connection roads only
        rows = []

        if self.intersection.internalConnectionRoads is None:
            raise Exception(f"{self.name}: missing internalConnectionRoads")
        
        for connectionRoad in self.intersection.internalConnectionRoads:
            # print(f"lenght of connection road: ", connectionRoad.length())
            turnComplexity = TurnComplexity.createFromRoad(connectionRoad, minPathLengthIntersection=self.minPathLengthIntersection)
            self.turnComplexities[connectionRoad] = turnComplexity.normalizedRadiusComplexity()
            self.connectionRoadCharacteristics[connectionRoad]['turnCurvature'] = turnComplexity.radiusComplexity()
            self.connectionRoadCharacteristics[connectionRoad]['turnCurvatureNorm'] = turnComplexity.normalizedRadiusComplexity()
            self.connectionRoadCharacteristics[connectionRoad]['turnLength'] = connectionRoad.length()

            fromRoad = connectionRoad.getExtendedPredecessorByRoadId(connectionRoad.predecessor.element_id).road
            stats = dict()
            stats['turnCurvature'] = turnComplexity.radiusComplexity()
            stats['turnCurvatureNorm'] = turnComplexity.normalizedRadiusComplexity()
            stats['turnLength'] = connectionRoad.length()
            # stats['fov'] = self.fovComplexity.incidentRoadCharacteristics[fromRoad]['fov']
            # stats['corner'] = self.fovComplexity.incidentRoadCharacteristics[fromRoad]['corner']
            # stats['cornerDeviation'] = self.fovComplexity.incidentRoadCharacteristics[fromRoad]['cornerDeviation']
            # stats['complexity'] = self.getComplexity(
            #                                             norm_curvature=stats['turnCurvatureNorm'],
            #                                             fov=stats['fov'],
            #                                             deviationFromfov=stats['cornerDeviation']
            #                                         )

            rows.append(stats)
        
        self.connectRoadDf = pd.DataFrame(rows)
        pass


    def getMaxTurnComplexity(self):
        if len(self.turnComplexities) == 0:
            self.measureTurnComplexities()
        
        return max(self.turnComplexities.values())

    
    def getComplexity(self, norm_curvature, fov, deviationFromfov):
        normFov = fov / 180 # assuming max is 180
        normDeviation = deviationFromfov / 90 #assuming max is 90
        complexity = norm_curvature * normFov * normDeviation
        return complexity