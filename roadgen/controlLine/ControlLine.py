from matplotlib.pyplot import disconnect
from numpy.core.fromnumeric import sort
from roadgen.controlLine.ControlPoint import ControlPoint
import math
import numpy as np
from typing import List
from skspatial.objects import Line, Point

class ControlLine:

    def __init__(self, id, start, end) -> None:

        self.name = f"ControlLine #{id}"
        self.id = id
        self.start = start
        self.end = end

        if self.start[0] > self.end[0]:
            raise Exception(f"{self.name}:Controlines start {self.start} must have lower x than end {self.end}")

        self.controlPoints = []

        self.len = math.sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)
        self.theta = self.getTheta()

        self.slopeSign = self.getSlopeSign()
        self.connectedExternalPoints = set([])
        self.isPointConnected = {}
        self.pointToLineMap = {} # list of lines each point has a connection to
        self._sortedPoints = None

        self.line = Line(point=self.start, direction=[self.end[0] - self.start[0], self.end[1] - self.start[1]])
        pass


    
    def __str__(self) -> str:

        pointStr = ""
        for point in self.controlPoints:
            pointStr += point.__str__()

        
        pointToLineMapStr = "Point to Line Map:"
        for point in self.pointToLineMap:
            lines = self.pointToLineMap[point]
            lineStr = ""
            for line in lines:
                lineStr += f"{line.id},"
            pointToLineMapStr += f"\n\t Point {id(point)} {point.position}: {lineStr}"




        return (
            f"\nid: {self.id}"
            f"\nstart: {self.start}"
            f"\nend: {self.end}"
            f"\nlength: {self.len}"
            f"\ntheta: {math.degrees(self.theta)}"
            f"\npoints: {pointStr}"
            f"\npointToLineMapStr: {pointToLineMapStr}"
        )
    
    def getTheta(self):
        x = self.end[0] - self.start[0]
        return math.acos(x / self.len)

    
    def getSlopeSign(self):

        if (self.end[0] - self.start[0]) == 0.0:
            if self.end[1] > self.start[1]:
                return 1
            return -1
        slope = (self.end[1] - self.start[1]) / (self.end[0] - self.start[0])
        slopeSign = 1 if slope >= 0 else - 1
        return slopeSign

    #region ControlPoint operations

    def getOrderedControlPoints(self, forceSort = False):
        """Returns ordered points

        Returns:
            [type]: [description]
        """
        if (forceSort == False) and (self._sortedPoints is not None) and (len(self._sortedPoints) == len(self.controlPoints)):
            return self._sortedPoints
        # sort again
        cp0 = ControlPoint(position=self.start)
        self._sortedPoints = sorted(self.controlPoints, key=lambda point: point.distanceFrom(cp0))
        return self._sortedPoints

    def getLastPoint(self):
        if len(self.controlPoints) == 0:
            return None
        return self.getOrderedControlPoints()[-1]

    def hasPoint(self, point:ControlPoint):
        return point in self.controlPoints


    def createControlPoint(self, position):
        cp = ControlPoint(position=(position[0], position[1]))
        self.controlPoints.append(cp)
        self.isPointConnected[cp] = False
        self.pointToLineMap[cp] = set([])
        self.getOrderedControlPoints(forceSort=True)
        return cp


    def createNextControlPoint(self, distance):
        """returns None if distance goes beyond the end

        Args:
            distance ([type]): [description]
        """

        if len(self.controlPoints) == 0:
            # create the first one
            x = self.start[0] + distance * math.cos(self.theta)
            y = self.start[1] + distance * math.sin(self.theta) * self.slopeSign
            if (x > self.end[0] + 0.01): # floating error
                raise Exception(f"{self.name}: createNextControlPoint: First control point is not on the line")
        else:
            lastCP = self.getOrderedControlPoints()[-1]
            x = lastCP.position[0] + distance * math.cos(self.theta)
            y = lastCP.position[1] + distance * math.sin(self.theta) * self.slopeSign
            if (x > self.end[0] + 0.01): # floating error
                raise Exception(f"{self.name}: createNextControlPoint: next control point is not on the line")

        return self.createControlPoint((x, y))


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
        
        self.getOrderedControlPoints(forceSort=True)


    def getNearestSibling(self, point: ControlPoint):
        """Returns the nearest sibling and distance on the line

        Args:
            point ([type]): A point on the line
        """

        sortedPoints = self.getOrderedControlPoints()
        if len(sortedPoints) < 2:
            return None, 0

        if point == sortedPoints[0]:
            return sortedPoints[1], point.distanceFrom(sortedPoints[1])
        if point == sortedPoints[-1]:
            return sortedPoints[-2], point.distanceFrom(sortedPoints[-2])

        index = sortedPoints.index(point)

        distanceBefore = point.distanceFrom(sortedPoints[index - 1])
        distanceAfter = point.distanceFrom(sortedPoints[index + 1])
        if distanceBefore < distanceAfter:
            return sortedPoints[index - 1], distanceBefore
        else:
            return sortedPoints[index + 1], distanceAfter
    
    
    def mergeWithNearestSiblingIfClose(self, mergeWho: ControlPoint, minSeparation):
        mergeWith, _ = self.getNearestSibling(mergeWho)
        if mergeWith is None:
            return mergeWho
        
        return self.mergeControlPointsIfClose(mergeWith=mergeWith, mergeWho=mergeWho, minSeparation=minSeparation)


    def mergeControlPointsIfClose(self, mergeWith: ControlPoint, mergeWho: ControlPoint, minSeparation):
        """Returns mergeWith if merged, mergeWho otherwise

        Args:
            mergeWith (ControlPoint): [description]
            mergeWho (ControlPoint): [description]
            minSeparation ([type]): [description]
        """
        distance = mergeWith.distanceFrom(mergeWho)
        if distance < minSeparation:
            self.mergeControlPoints(mergeWith=mergeWith, mergeWho=mergeWho)
            return mergeWith
        return mergeWho
        

    def mergeControlPoints(self, mergeWith: ControlPoint, mergeWho: ControlPoint):
        # copy adjacent points
        # copy line mappings
        # delete from isPointConnected
        # delete from sorted
        # delete from points

        mergeWith.addAdjacents(mergeWho.adjacentPoints)
        self.pointToLineMap[mergeWith].update(self.pointToLineMap[mergeWho])
        self.deleteControlPoint(mergeWho)


    def deleteControlPoint(self, point):
        self.pointToLineMap.pop(point, None)
        self.isPointConnected.pop(point, None)
        self._sortedPoints.remove(point)
        self.controlPoints.remove(point)

    #endregion


    #region connection operations

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
    

    #endregion

    #region external-points

    def getProjection(self, externalPointPos):
        """Returns None if the projection is not inside the line segment. Returns an array x,y coordinates

        Args:
            externalPoint ([type]): [description]
        """
        if externalPointPos in self.controlPoints:
            raise Exception(f"{self.name}: getProjection: externalPointPos must not exist on the control line")
        projectionPoint = self.line.project_point(externalPointPos)
        if projectionPoint[0] < self.start[0] or projectionPoint[0] > self.end[0]:
            return None
        # if projectionPoint[1] < self.start[1] or projectionPoint[1] > self.end[1]:
        #     return None
        
        return projectionPoint
    

    def isProjectionInsideControlPoints(self, projection):
        """Checks if a projection is between existing control points.

        Args:
            projection ([type]): [description]

        Returns:
            [type]: [description]
        """
        lastCp = self.getLastPoint()
        if lastCp.position[0] > projection[0]:
            return True
        return False


    def distanceFrom(self, externalPoint):
        return self.line.distance_point(externalPoint)



    def nearestFromExternal(self, externalPoint):
        """Finds the nearest control point on this line from externalPoint which is not on this line.

        Args:
            externalPoint ([type]): [description]
        """
        pass

    
    def nearestFree(self, anotherPoint):
        pass


    def nearestOrphan(self, anotherPoint):
        pass

    #endregion