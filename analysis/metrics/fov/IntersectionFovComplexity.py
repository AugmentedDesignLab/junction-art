from junctions.Intersection import Intersection
from extensions.ExtendedRoad import ExtendedRoad
import extensions
import math
from analysis.metrics.fov.Angle import Angle
from analysis.metrics.fov.Fov import Fov
from analysis.metrics.fov.FovComplexity import FovComplexity

class IntersectionFovComplexity:

    def __init__(self, intersection: Intersection) -> None:
        self.intersection = intersection
        self.incidentRoadCharacteristics = {}
        self.initIncidentRoadCharacteristics()
        self.minCornerAngle = None
        self.maxDeviationAngle = None
        self.maxFov = None
        self.measureCorners()
        self.name = f"IntersectionFovComplexity #{self.intersection.id}"

    
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
            self.measureCorners()
        return self.minCornerAngle


    def measureCorners(self):
        
        for incidentCP, incidentRoad in zip(self.intersection.incidentCPs, self.intersection.incidentRoads):

            otherCP = extensions.reverseCP(incidentCP)
            p0x, p0y, _ = incidentRoad.getPosition(otherCP)
            p1x, p1y, _ = incidentRoad.getPosition(incidentCP)
            p0 = (p0x, p0y)
            p1 = (p1x, p1y)
            cornerAngle, deviationAngle = self.measureMinCornerAndDeviationFrom(incidentRoad, p0, p1)
            fov = Fov.getFovFromMinCorner(cornerAngle)

            self.incidentRoadCharacteristics[incidentRoad]['corner'] = cornerAngle
            self.incidentRoadCharacteristics[incidentRoad]['cornerDeviation'] = deviationAngle
            self.incidentRoadCharacteristics[incidentRoad]['fov'] = fov

            # intersection summary
            if (self.maxFov is None) or (self.maxFov < fov):
                self.maxFov = fov

            if (self.minCornerAngle is None) or (cornerAngle < self.minCornerAngle):
                self.minCornerAngle = cornerAngle
            
            if (self.maxDeviationAngle is None) or (self.maxDeviationAngle < deviationAngle):
                self.maxDeviationAngle = deviationAngle
            
            pass
        pass

    
    def measureMinCornerAndDeviationFrom(self, fromRoad: ExtendedRoad, p0, p1):

        minAngle = 3.15
        maxDeviation = 0
        for incidentCP, incidentRoad in zip(self.intersection.incidentCPs, self.intersection.incidentRoads):
            if incidentRoad == fromRoad:
                continue

            otherCP = extensions.reverseCP(incidentCP)
            p2x, p2y, _ = incidentRoad.getPosition(incidentCP)
            p3x, p3y, _ = incidentRoad.getPosition(otherCP)
            p2 = (p2x, p2y)
            p3 = (p3x, p3y)
            angle = Angle.cornerAngle(p0, p1, p2)
            deviationAngle = FovComplexity.getAngleDeviationFromSightLine(p1, p2, p3)

            print(f"{self.name}: p0 = ({p0}), p1 = ({p1}), p2 = ({p2}), p2 = ({p3})")
            print(f"{self.name}: Corner angle between road {fromRoad.id} and {incidentRoad.id} is {math.degrees(angle)}. Deviation is {math.degrees(deviationAngle)}")

            if angle < minAngle:
                minAngle = angle
            if maxDeviation < deviationAngle:
                maxDeviation = deviationAngle
        
        return minAngle




