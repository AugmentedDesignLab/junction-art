import numpy as np
import pyodrx
from junctionart.extensions.ExtendedRoad import ExtendedRoad
import math

class TurnComplexity:


    def __init__(self, changeInHeading, lengthOfPath, minPathLengthIntersection=10) -> None:

        self.changeInHeading = changeInHeading
        self.lengthOfPath = lengthOfPath
        self.maxComplexity = np.pi / minPathLengthIntersection
        pass

    
    def __str__(self) -> str:
        return(
            f"\tradius-complexity: {self.radiusComplexity()}"
            f" radius-complexity-normalized: {self.normalizedRadiusComplexity()}"
        )

    def radiusComplexity(self):
        # print(f"change in heading ={math.degrees(self.changeInHeading)}, length = {self.lengthOfPath}")
        return round(self.changeInHeading / self.lengthOfPath, 2)
    

    def normalizedRadiusComplexity(self):
        return round(self.radiusComplexity() / self.maxComplexity, 2)

    @staticmethod
    def createFromRoad(road: ExtendedRoad, minPathLengthIntersection=10):

        _, _, startH = road.getPosition(pyodrx.ContactPoint.start)
        _, _, endH = road.getPosition(pyodrx.ContactPoint.end)
        length = road.length()

        changeInHeading = abs(startH - endH)

        return TurnComplexity(changeInHeading=changeInHeading, lengthOfPath=length, minPathLengthIntersection=minPathLengthIntersection)