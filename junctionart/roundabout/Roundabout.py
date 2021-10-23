from junctions.Intersection import Intersection
from extensions.ExtendedRoad import ExtendedRoad
from typing import List
# holds a roundabout object similar to intersection

class Roundabout(Intersection):

    def __init__(self, id, incidentRoads, incidentCPs, geoConnectionRoads=None, internalConnectionRoads: List[ExtendedRoad] = None, odr=None):
        super().__init__(id, incidentRoads, incidentCPs, geoConnectionRoads=geoConnectionRoads, internalConnectionRoads=internalConnectionRoads, odr=odr)

        self.internalSegments = []
        self.intersections = {} # keys are incident point object, and values are a 3 way intersections

    pass
