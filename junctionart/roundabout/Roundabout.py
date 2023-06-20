import os
from junctionart import extensions
from junctionart.library.Configuration import Configuration
from junctionart.roundabout.RewardUtil import RewardUtil

class Roundabout():

    def __init__(self, id, countryCode, laneWidth, center, radius, offsets, straightRoads, incomingConnectionRoads, outgoingConnectionRoads, circularRoadLanes, circularRoadStartPoints, circularRoads, junctions, odr):
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
        self.circularRoadStartPoints = circularRoadStartPoints
        self.circularRoads = circularRoads
        self.junctions = junctions
        self.odr = odr

    def showRoundabout(self):
        config = Configuration()
        extensions.view_road(self.odr, os.path.join("..", config.get("esminipath")))

    def getReward(self):
        return RewardUtil.score(self)