from junctionart.junctions.Intersection import Intersection
import pyodrx
import numpy as np
import math, os
import logging
import junctionart.extensions as extensions
from junctionart.library.Configuration import Configuration

class IntersectionValidator:

    def __init__(self, debug=True) -> None:
        self.name = "IntersectionValidator"
        self.debug = debug
        self.configuration = Configuration()
        pass

    
    def validateIncidentPoints(self, intersection: Intersection, minDistance=None) -> bool:

        if intersection.incidentCPs[0] != pyodrx.ContactPoint.end:
            raise Exception(f"{self.name}: validator not implemented for first road with start as IP")

        valid = True
        if minDistance is not None:
            valid = self.validateMinDistanceBetweenIncidentPoints(intersection, minDistance)
        
        if valid == False:
            # extensions.view_road(intersection.odr, os.path.join('..',self.configuration.get("esminipath")))
            # exit()
            return False
        
        if self.validateDirectionAndPositionAgreement(intersection) == False:
            # extensions.view_road(intersection.odr, os.path.join('..',self.configuration.get("esminipath")))
            # exit()
            return False
        

        
        return True

    
    def validateMinDistanceBetweenIncidentPoints(self, intersection: Intersection, minConnectionLength):

        for i in range(len(intersection.incidentRoads)-2):
            road1 = intersection.incidentRoads[i]
            road2 = intersection.incidentRoads[i + 2]
            cp1 = intersection.incidentCPs[i]
            cp2 = intersection.incidentCPs[i + 2]

            x1, y1, h1 = road1.getPosition(cp1)
            x2, y2, h2 = road2.getPosition(cp2)

            distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) * 1.2 # 1.2 offset for param poly.

            if distance < minConnectionLength:
                logging.debug("IntersectionValidator: invalid distance {distance} < {minConnectionLength}")
                return False

        return True

    
    def validateDirectionAndPositionAgreement(self, intersection: Intersection):
        """If the heading of the last point is going south west, the point must be under x axis. Assumes the intersection is not rotated and first road is on x axis

        Args:
            intersection (Intersection): [description]
        """

        firstRoad = intersection.incidentRoads[0]
        x, y, h = firstRoad.getPosition(intersection.incidentCPs[0])

        h = h % (np.pi * 2)
        # h = math.ceil((h + np.pi * 2) % np.pi)
        # if h != 3 and h != 0:
        #     raise Exception(f"{self.name}: validateDirectionAndPositionAgreement: cannot validated rotated intersection h = {h}")
        

        # get the last incident roads position and heading
        lastIncidentRoad = intersection.incidentRoads[-1]
        lastIP = intersection.incidentCPs[-1]
        lastX, lastY, lastH = lastIncidentRoad.getPosition(lastIP)

        lastH = lastH % (np.pi * 2)



        # validate X. border of the last road cannot go beyond x
        borderDistanceLast = lastIncidentRoad.getBorderDistanceRight(lastIP)
        if lastIP == pyodrx.ContactPoint.end:
            borderDistanceLast = lastIncidentRoad.getBorderDistanceLeft(lastIP)

        if (lastX - borderDistanceLast) < x:
            logging.debug("IntersectionValidator: invalid X pos")
            return False


        borderDistanceFirst = firstRoad.getBorderDistanceRight(intersection.incidentCPs[0])
        if intersection.incidentCPs[0] == pyodrx.ContactPoint.end:
            borderDistanceFirst = lastIncidentRoad.getBorderDistanceLeft(intersection.incidentCPs[0])

        # validate Y
        minH = h + np.pi
        maxH = (h + (3/2) * np.pi)
        if lastH > minH and lastH < maxH:
            if lastY >= (y - borderDistanceFirst):
                logging.debug("IntersectionValidator: invalid Y pos")
                return False
        
        return True
        




        
