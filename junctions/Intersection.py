import pyodrx
import numpy as np

class Intersection:

    def __init__(self, id, incidentRoads, incidentCPs, geoConnectionRoads=None, odr=None):

        self.id = id
        self.incidentRoads = incidentRoads
        self.incidentCPs = incidentCPs
        self.geoConnectionRoads = geoConnectionRoads
        self.odr = odr
        self.incidentPoints = self.getIncidentPoints()

    
    def setOdr(self, odr):
        self.odr = odr

    
    def getIncidentPoints(self):

        """REturns incident points with heading always going out of the intersection
        """

        ips = []

        for _, (road, cp) in enumerate(zip(self.incidentRoads, self.incidentCPs)):
            x, y, h = road.getPosition(cp)
            if cp == pyodrx.ContactPoint.end:
                h = (h + np.pi) % (np.pi *2)
            ips.append((x, y, h))
        
        return ips


    def getIncidentPointsTranslatedToCenter(self):
        """First incident point is translated to center (0,0)
        """
        transX = -self.incidentPoints[0][0]
        transY = self.incidentPoints[0][1]

        translatedIPs = []

        for ip in self.incidentPoints:
            x = ip[0] + transX
            y = ip[1] + transY
            translatedIPs.append((x, y, ip[2]))
        
        return translatedIPs


    def getWH(self, mode='incident-point', padding=5):
        """returns width and height. Assumes incidents road has almost 0 length for simplicity

        Args:
            odr ([type]): [description]
            padding: in meters. in case of a 3-way, all the incident points can be so close to each other that some connection road may have an extreme point. So, we add a safe padding.
        """

        # corner case. in case of a 3-way, all the incident points can be so close to each other that some connection road may have an extreme point. So, we add a safe padding.

        (minX, minY), (maxX, maxY) = self.getBBox(translateToCenter=False, mode=mode, padding=padding)
        
        return maxX - minX, maxY - minY

    

    def getBBox(self, translateToCenter=True, mode='incident-point', padding=5):

        incidentPoints = self.incidentPoints
        if translateToCenter:
            incidentPoints = self.getIncidentPointsTranslatedToCenter()

        
        minX = 99999999
        maxX = -99999999
        minY = 99999999
        maxY = -99999999

        if mode == 'incident-point':
            for ip in self.incidentPoints:
                if ip[0] < minX:
                    minX = ip[0]
                if ip[1] < minY:
                    minY = ip[1]
                if ip[0] > maxX:
                    maxX = ip[0]
                if ip[1] > maxY:
                    maxY = ip[1]
        
        minX -= padding
        minY -= padding

        maxX += padding
        maxY += padding
        
        return (minX, minY), (maxX, maxY)
        




            


