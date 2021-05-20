from pyodrx.enumerations import ContactPoint
import pyodrx
from roadgen.definitions.DirectionIntersection import DirectionIntersection
import numpy as np
from roadgen.definitions.DirectionQuadrant import DirectionQuadrantType
from roadgen.definitions.DirectionQuadrant import DirectionQuadrant
from extensions.CountryCodes import CountryCodes
from junctions.LaneConfiguration import LaneConfiguration
from junctions.Intersection import Intersection

class IntersectionAdapter:

    def __init__(self, countryCode=CountryCodes.US):
        self.countryCode = countryCode
        pass


    def intersectionTo4DirectionIntersection(self, intersection: Intersection) -> DirectionIntersection:

        #1. TODO if not adjusted, adjust

        #2. find the minimum bounding box
        botLeft, topRight = intersection.getBBox(translateToCenter=True)

        #3. find the center of the bounding box
        centerX = (botLeft[0] + topRight[0]) / 2
        centerY = (botLeft[1] + topRight[1]) / 2

        #4. assign direction based on the position of the incident points

        translatedIPs = intersection.getIncidentPointsTranslatedToCenter()


        #5. adjust direction based on the heading.

        # direction quadrants

        top = DirectionQuadrant(nIncoming=0, nOutgoing=0)
        left = DirectionQuadrant(nIncoming=0, nOutgoing=0)
        bot = DirectionQuadrant(nIncoming=0, nOutgoing=0)
        right = DirectionQuadrant(nIncoming=0, nOutgoing=0)

        for _, (ip, road, cp) in enumerate(zip(translatedIPs, intersection.incidentRoads, intersection.incidentCPs)):
            # TODO, this might lead to problems are we are taking incident points CPs which may have different number of lanes than the other CPs. We need to keep it fixed or get the other cp.

            otherCP = pyodrx.ContactPoint.start if (cp == pyodrx.ContactPoint.end) else pyodrx.ContactPoint.end

            nIncoming = len(LaneConfiguration.getIncomingLanesOnARoad(road, otherCP, self.countryCode))
            nOutgoing = len(LaneConfiguration.getOutgoingLanesOnARoad(road, otherCP, self.countryCode))

            quadrantType = self.getQuadrant(centerX, centerY, ip)
            if quadrantType == DirectionQuadrantType.TOP:
                top.nIncoming += nIncoming
                top.nOutgoing += nOutgoing
                top.roads[road] = otherCP
            if quadrantType == DirectionQuadrantType.LEFT:
                left.nIncoming += nIncoming
                left.nOutgoing += nOutgoing
                left.roads[road] = otherCP
            if quadrantType == DirectionQuadrantType.BOT:
                bot.nIncoming += nIncoming
                bot.nOutgoing += nOutgoing
                bot.roads[road] = otherCP
            if quadrantType == DirectionQuadrantType.RIGHT:
                right.nIncoming += nIncoming
                right.nOutgoing += nOutgoing
                right.roads[road] = otherCP
            
        return DirectionIntersection(top=top, left=left, bot=bot, right=right)



    def getQuadrant(self, centerX, centerY, ip):

        x, y, h = ip
        
        h = h % (np.pi * 2)
        if h < 0:
            h = (np.pi * 2) + h

        if h <= np.pi * 0.25:
            return DirectionQuadrantType.RIGHT
        if h <= np.pi * 0.75:
            return DirectionQuadrantType.TOP
        if h < np.pi * 1.25:
            return DirectionQuadrantType.LEFT
        if h < np.pi * 1.75:
            return DirectionQuadrantType.BOT

        return DirectionQuadrantType.RIGHT



