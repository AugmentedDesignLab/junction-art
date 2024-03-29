from junctionart.junctions.Intersection import Intersection
from junctionart.extensions.ExtendedRoad import ExtendedRoad
import junctionart.extensions
import math
from analysis.metrics.fov.Angle import Angle
from analysis.metrics.fov.FovComplexity import FovComplexity

class IntersectionCorners:

    
    def __init__(self, intersection: Intersection) -> None:
        self.intersection = intersection
        self.corners = {}
        self.minAngle = None
        self.name = f"IntersectionCorners #{self.intersection.id}"
        pass


    def getMinCornerAngle(self):
        if self.minAngle is None:
            self.measureCorners()
        return self.minAngle


    def measureCorners(self):
        
        for incidentCP, incidentRoad in zip(self.intersection.incidentCPs, self.intersection.incidentRoads):

            otherCP = extensions.reverseCP(incidentCP)
            p0x, p0y, _ = incidentRoad.getPosition(otherCP)
            p1x, p1y, _ = incidentRoad.getPosition(incidentCP)
            p0 = (p0x, p0y)
            p1 = (p1x, p1y)
            self.corners[incidentRoad] = self.measureMinCornerFrom(incidentRoad, p0, p1)


    
    def measureMinCornerFrom(self, fromRoad: ExtendedRoad, p0, p1):

        minAngle = 3.15
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
        
        if (self.minAngle is None) or (minAngle < self.minAngle):
            self.minAngle = minAngle

        return minAngle




