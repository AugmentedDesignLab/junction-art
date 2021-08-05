from junctions.Intersection import Intersection
from analysis.metrics.intersection_complexity.TurnComplexity import TurnComplexity

class IntersectionComplexity:

    def __init__(self, intersection: Intersection) -> None:
        self.intersection = intersection
        self.turnComplexities = {}
        self.name = f"IntersectionComplexity #{self.intersection.id}"
        pass


    def measureTurnComplexities(self):
        # find the left and right turn roads
        # measure complexities

        # We need to do it for connection roads only

        if self.intersection.internalConnectionRoads is None:
            raise Exception(f"{self.name}: missing internalConnectionRoads")
        
        for connectionRoad in self.intersection.internalConnectionRoads:
            self.turnComplexities[connectionRoad] = TurnComplexity.createFromRoad(connectionRoad)