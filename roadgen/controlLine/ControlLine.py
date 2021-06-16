from matplotlib.pyplot import disconnect
from roadgen.controlLine.ControlPoint import ControlPoint
import math
import numpy as np
from typing import List

class ControlLine:

    def __init__(self, id, start, end) -> None:

        self.id = id
        self.start = start
        self.end = end
        self.controlPoints = []

        self.len = math.sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)
        self.theta = self.getTheta()

        self.slopeSign = self.getSlopeSign()
        self.connectedExternalPoints = set([])
        self.isPointConnected = {}
        self.pointToLineMap = {} # list of lines each point has a connection to
        pass


    
    def __str__(self) -> str:

        pointStr = ""
        for point in self.controlPoints:
            pointStr += point.__str__()

        return (
            f"\nid: {self.id}"
            f"\nstart: {self.start}"
            f"\nend: {self.end}"
            f"\nlength: {self.len}"
            f"\ntheta: {math.degrees(self.theta)}"
            f"\npoints: {pointStr}"
        )
    
    def getTheta(self):
        x = self.end[0] - self.start[0]
        return math.acos(x / self.len)

    
    def getSlopeSign(self):

        if (self.end[0] - self.start[0]) == 0.0:
            return 1
        slope = (self.end[1] - self.start[1]) / (self.end[0] - self.start[0])
        slopeSign = 1 if slope >= 0 else - 1
        return slopeSign


    def getOrderedControlPoints(self):
        return self.controlPoints

    def hasPoint(self, point:ControlPoint):
        return point in self.controlPoints


    def createControlPoints(self, maxNumOfControlPoints, minDistance, maxDistance, p=[0.8, 0.1, 0.1]):
        """improve later

        Args:
            n ([type]): [description]
            minDistance ([type]): [description]
            MaxDistance ([type]): [description]
        """

        x = self.start[0]
        y = self.start[1]
        for i in range(maxNumOfControlPoints):
            # distance = np.random.uniform(minDistance, maxDistance)
            distance = np.random.choice([75, 75, 100], p=p)
            # distance = 50
            x = x + distance * math.cos(self.theta)
            y = y + distance * math.sin(self.theta) * self.slopeSign

            if (x > self.end[0] + 0.01): # floating error
                break
            cp = ControlPoint(position=(x, y))
            self.controlPoints.append(cp)
            self.isPointConnected[cp] = False
            self.pointToLineMap[cp] = set([])


    def createConnection(self, anotherLine, myPoint: ControlPoint, anotherPoint: ControlPoint):
        self.connectedExternalPoints.add(anotherPoint)
        self.isPointConnected[myPoint] = True
        self.pointToLineMap[myPoint].add(anotherLine)
        myPoint.addAdjacent(anotherPoint)


    def hasConnection(self, anotherPoint):
        if anotherPoint in self.connectedExternalPoints:
            return True

    def pointsConnectedTo(self, anotherLine) -> List[ControlPoint]:

        connectedPoints = []
        for point in self.controlPoints:
            if anotherLine in self.pointToLineMap[point]:
                connectedPoints.append(point)

        return connectedPoints

    def pointsNotConnectedTo(self, anotherLine) -> List[ControlPoint]:

        disconnectedPoints = []
        for point in self.controlPoints:
            if anotherLine not in self.pointToLineMap[point]:
                disconnectedPoints.append(point)

        return disconnectedPoints
    



    def nearest(self, anotherPoint):
        """Finds the nearest control point on this line from anotherPoint

        Args:
            anotherPoint ([type]): [description]
        """
        pass

    
    def nearestFree(self, anotherPoint):
        pass


    def nearestOrphan(self, anotherPoint):
        pass