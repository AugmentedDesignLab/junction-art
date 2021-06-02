from enum import Enum, auto
import math


class ControlPointColor(Enum):
    GREEN = auto()
    RED = auto()
    PURPLE = auto()
    pass

class ControlPoint:

    def __init__(self, position, color=ControlPointColor.GREEN) -> None:
        self.color = color
        self.position = position
        self.adjacentPoints = []


    def __str__(self) -> str:
        return (
            f"\n\tposition: {self.position}"
            f"\n\tcolor: {self.color}"
        )

    
    def addAdjacent(self, anotherPoint):
        if anotherPoint not in self.adjacentPoints:
            self.adjacentPoints.append(anotherPoint)
    
    def reOrderAjacentPoints(self):
        raise NotImplementedError()

    
    def isConnected(self):
        return len(self.adjacentPoints) > 0
    
    def nConnections(self):
        return len(self.adjacentPoints)

    
    def distanceFrom(self, anotherPoint):

        xDiff = self.position[0] - anotherPoint.position[0]
        yDiff = self.position[1] - anotherPoint.position[1]

        return math.sqrt(xDiff ** 2 + yDiff ** 2)

