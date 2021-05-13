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

            nIncoming = len(LaneConfiguration.getIncomingLanesOnARoad(road, cp, self.countryCode))
            nOutgoing = len(LaneConfiguration.getOutgoingLanesOnARoad(road, cp, self.countryCode))

            quadrantType = self.getQuadrant(centerX, centerY, ip)
            if quadrantType == DirectionQuadrantType.TOP:
                top.nIncoming += nIncoming
                top.nOutgoing += nOutgoing
            if quadrantType == DirectionQuadrantType.LEFT:
                left.nIncoming += nIncoming
                left.nOutgoing += nOutgoing
            if quadrantType == DirectionQuadrantType.BOT:
                bot.nIncoming += nIncoming
                bot.nOutgoing += nOutgoing
            if quadrantType == DirectionQuadrantType.RIGHT:
                right.nIncoming += nIncoming
                right.nOutgoing += nOutgoing
            
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

        # if y <= centerY:
        #     # if a point is under horiziontal center line
        #     ## if heading is between 225 and 315, the incident point is at bot
        #     ## if heading < 225,left
        #     ## else right
        #     if h < np.pi * 1.25:
        #         return DirectionQuadrantType.LEFT
            


        # else:
        #     # if a point is under horiziontal center line
        #     ## if heading is between 225 and 315, the incident point is at bot
        #     ## if heading < 225,left
        #     ## else right
            # pass
