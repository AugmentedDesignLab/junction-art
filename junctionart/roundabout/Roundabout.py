class Roundabout():

    def __init__(self, id, countryCode, laneWidth, center, radius, offsets, straightRoads, incomingConnectionRoads, outgoingConnectionRoads, circularRoadLanes, circularRoads, junctions, odr):
        self.id = id
        self.countryCode = countryCode
        self.landWidth = laneWidth
        self.center = center
        self.radius = radius
        self.offsets = offsets
        self.straightRoads = straightRoads
        self.incomingConnectionRoads = incomingConnectionRoads
        self.outgoingConnectionRoads = outgoingConnectionRoads
        self.circularRoadLanes = circularRoadLanes
        self.circularRoads = circularRoads
        self.junctions = junctions
        self.odr = odr

