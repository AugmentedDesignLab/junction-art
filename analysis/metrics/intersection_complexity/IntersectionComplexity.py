from junctions.Intersection import Intersection
from analysis.metrics.intersection_complexity.TurnComplexity import TurnComplexity

class IntersectionComplexity:


    def __init__(self, intersection: Intersection, minPathLengthIntersection=10) -> None:
        self.intersection = intersection
        self.minPathLengthIntersection = minPathLengthIntersection
        self.turnComplexities = {}
        self.name = f"IntersectionComplexity #{self.intersection.id}"
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

        if self.intersection.internalConnectionRoads is None:
            raise Exception(f"{self.name}: missing internalConnectionRoads")
        
        for connectionRoad in self.intersection.internalConnectionRoads:
            # print(f"lenght of connection road: ", connectionRoad.length())
            self.turnComplexities[connectionRoad] = TurnComplexity.createFromRoad(connectionRoad, minPathLengthIntersection=self.minPathLengthIntersection).normalizedRadiusComplexity()
        pass


    def getMaxTurnComplexity(self):
        if len(self.turnComplexities) == 0:
            self.measureTurnComplexities()
        
        return max(self.turnComplexities.values())