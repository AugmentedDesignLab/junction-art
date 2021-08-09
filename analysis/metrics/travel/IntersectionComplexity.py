from junctions.Intersection import Intersection
from analysis.metrics.travel.TurnComplexity import TurnComplexity
from shapely.geometry import Polygon

class IntersectionComplexity:


    def __init__(self, intersection: Intersection, minPathLengthIntersection=10) -> None:
        self.intersection = intersection
        self.minPathLengthIntersection = minPathLengthIntersection
        self.connectionRoadCharacteristics = {}
        self.turnComplexities = {}
        self.measureTurnComplexities()
        self.area = self.measureArea()
        self.name = f"IntersectionComplexity #{self.intersection.id}"
        pass


    def measureArea(self):
        
        vertices = []
        for incidentCP, incidentRoad in zip(self.intersection.incidentCPs, self.intersection.incidentRoads):
            x, y, _ = incidentRoad.getPosition(incidentCP)
            vertices.append((x, y))
        
        poly = Polygon(vertices)
        return poly.area

    
    
    def initConnectionRoadCharacteristics(self):

        if self.intersection.internalConnectionRoads is None:
            raise Exception(f"{self.name}: missing internalConnectionRoads")

        for road in self.intersection.internalConnectionRoads:
            self.connectionRoadCharacteristics[road] = {
                'turnRadius' : None,
                'turnComplexity' : None,
                'turnLength' : None
            }
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
            turnComplexity = TurnComplexity.createFromRoad(connectionRoad, minPathLengthIntersection=self.minPathLengthIntersection)
            self.turnComplexities[connectionRoad] = turnComplexity.normalizedRadiusComplexity()
            self.connectionRoadCharacteristics[connectionRoad]['turnRadius'] = turnComplexity.radiusComplexity()
            self.connectionRoadCharacteristics[connectionRoad]['turnComplexity'] = turnComplexity.normalizedRadiusComplexity()
        pass


    def getMaxTurnComplexity(self):
        if len(self.turnComplexities) == 0:
            self.measureTurnComplexities()
        
        return max(self.turnComplexities.values())