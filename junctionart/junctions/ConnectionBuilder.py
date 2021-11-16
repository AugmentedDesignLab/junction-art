import pyodrx
import junctionart.extensions as extensions
import math
import numpy as np
from junctionart.library.Configuration import Configuration
from junctionart.extensions.CountryCodes import CountryCodes
from junctionart.junctions.CurveRoadBuilder import CurveRoadBuilder
from junctionart.junctions.Geometry import Geometry
from scipy.interpolate import CubicHermiteSpline
from junctionart.junctions.LaneSides import LaneSides
from junctionart.junctions.RoadLinker import RoadLinker
from junctionart.junctions.LaneConfiguration import LaneConfiguration
from junctionart.junctions.LaneConfigurationStrategies import LaneConfigurationStrategies
import logging

class ConnectionBuilder:


    def __init__(self):
        self.config = Configuration()
        self.countryCode = CountryCodes.getByStr(self.config.get("countryCode"))
        self.curveBuilder = CurveRoadBuilder()
        self.name = "ConnectionBuilder"
        self.uTurnFirstLaneShift = self.config.get("uturn_firstlane_shift")
        

    
    def createSingleLaneConnectionRoad(self, newRoadId, incomingRoad, outgoingRoad, incomingLaneId, outgoingLaneId, incomingCp, outgoingCp):
        """Warining: uses default lane width. Works only after roads has been adjusted.

        Args:
            incomingRoad ([type]): [description]
            outgoingRoad ([type]): [description]
            incomingLaneId ([type]): [description]
            outgoingLaneId ([type]): [description]
            incomingCp ([type]): [description]
            outgoingCp ([type]): [description]
        """
        laneSides = None
        connectionLaneId = None
        if self.countryCode == CountryCodes.US:
            laneSides = LaneSides.RIGHT
            connectionLaneId = -1
        if self.countryCode == CountryCodes.UK:
            laneSides = LaneSides.LEFT
            connectionLaneId = 1
        
        incomingBoundaryId = incomingLaneId - 1
        if incomingLaneId < 0:
            incomingBoundaryId = incomingLaneId + 1

        outgoingBoundaryId = outgoingLaneId - 1
        if outgoingLaneId < 0:
            outgoingBoundaryId = outgoingLaneId + 1

        # TODO, get lane widths from road and create an equation.
        width = self.config.get("default_lane_width")
        

        x1, y1, h1 = incomingRoad.getLanePosition(incomingBoundaryId, incomingCp)
        x2, y2, h2 = outgoingRoad.getLanePosition(outgoingBoundaryId, outgoingCp)

        # special case for U turns from -1 to 1 or 1 to -1
        if x1 == x2 and y1 == y2:
        #     x1 = 0.9 * x1
        #     y1 = 0.9 * y1
            width -= self.uTurnFirstLaneShift

        logging.debug(f"{self.name}: createSingleLaneConnectionRoad: start: ", x1, y1, h1)
        logging.debug(f"{self.name}: createSingleLaneConnectionRoad: end: ", x2, y2, h2)

        xCoeffs, yCoeffs = Geometry.getCoeffsForParamPoly(x1, y1, h1, x2, y2, h2, incomingCp, outgoingCp, vShiftForSamePoint=self.uTurnFirstLaneShift)

        # scipy coefficient and open drive coefficents have opposite order.
        newConnection = self.curveBuilder.createParamPoly3(
                                                newRoadId, 
                                                isJunction=True,
                                                au=xCoeffs[3],
                                                bu=xCoeffs[2],
                                                cu=xCoeffs[1],
                                                du=xCoeffs[0],
                                                av=yCoeffs[3],
                                                bv=yCoeffs[2],
                                                cv=yCoeffs[1],
                                                dv=yCoeffs[0],
                                                n_lanes=1,
                                                lane_offset=width,
                                                laneSides=laneSides

                                            )

        
        newConnection.predecessorOffset = incomingBoundaryId

        newConnection.isSingleLaneConnection = True

        RoadLinker.createExtendedPredSuc(predRoad=incomingRoad, predCp=incomingCp, sucRoad=newConnection, sucCP=pyodrx.ContactPoint.start)

        RoadLinker.createExtendedPredSuc(predRoad=newConnection, predCp=pyodrx.ContactPoint.end, sucRoad=outgoingRoad, sucCP=outgoingCp)

        newConnection.predefinedLaneLinks.append(('predecessor', incomingLaneId, connectionLaneId))
        newConnection.predefinedLaneLinks.append(('successor', outgoingLaneId, connectionLaneId))
        

        return newConnection


    def createSingleLaneConnectionRoads(self, nextRoadId, outsideRoads, cp1, strategy):
        """Assumes all roads are connected by start point except for the first one

        Args:
            outsideRoads ([type]): [description]
            cp1 ([type]): [description]

        Returns:
            [type]: [description]
        """
        # return []

        roadDic = {}
        for road in outsideRoads:
            roadDic[road.id] = road

        newConnectionRoads = []        
        
        firstRoadId = outsideRoads[0].id

        countOldRoads = len(outsideRoads)

        # count = 0

        for incomingRoad in outsideRoads:

            # count += 1
            # if count == 1:
            #     continue

            incomingLaneIds = []
            if firstRoadId == incomingRoad.id:
                incomingLaneIds = LaneConfiguration.getIncomingLaneIdsOnARoad(incomingRoad, cp1, self.countryCode)
            else:
                incomingLaneIds = LaneConfiguration.getIncomingLaneIdsOnARoad(incomingRoad, pyodrx.ContactPoint.start, self.countryCode)
            
            outgoingLaneIds = LaneConfiguration.getOutgoingLanesIdsFromARoad(incomingRoad, outsideRoads, cp1=cp1, countryCode=self.countryCode)

            try:
                linkConfig = LaneConfiguration.getIntersectionLinks1ToMany(incomingLaneIds, outgoingLaneIds, strategy=strategy)

                incomingRoad.linkConfig = linkConfig

                # print(f"road id is {incomingRoad.id}")
                # print(linkConfig)

                # for each link, create a new connection road
                connectionRoadsForConfig = self.createRoadsForLinkConfig(nextRoadId, roadDic, firstRoadId, incomingRoad, cp1, linkConfig)
                nextRoadId += len(connectionRoadsForConfig)
                newConnectionRoads += connectionRoadsForConfig
            except Exception as e:
                logging.warn(f"{self.name}: {e}")
                raise e
            # break
            

        return newConnectionRoads     

    def createUTurnConnectionRoads(self, nextRoadId, outsideRoads, cp1, strategy=LaneConfigurationStrategies.SPLIT_FIRST):

        # return []
        
        roadDic = {}
        for road in outsideRoads:
            roadDic[road.id] = road

        newConnectionRoads = []        
        
        firstRoadId = outsideRoads[0].id

        incomingLaneIds = []

        cp = None
        for incomingRoad in outsideRoads:
            if firstRoadId == incomingRoad.id:
                cp = cp1
            else:
                cp = pyodrx.ContactPoint.start
            incomingLaneIds = LaneConfiguration.getIncomingLaneIdsOnARoad(incomingRoad, cp, self.countryCode)
            outgoingLaneIds = LaneConfiguration.getOutgoingLaneIdsOnARoad(incomingRoad, cp, self.countryCode)

            if len(incomingLaneIds) == 0 or len(outgoingLaneIds) == 0:
                continue

            incomingLaneIds = [incomingLaneIds[0]] # only the median lane
            
            try:
                linkConfig = LaneConfiguration.getIntersectionLinks1ToMany(incomingLaneIds, outgoingLaneIds, strategy=strategy)
                connectionRoadsForConfig = self.createRoadsForLinkConfig(nextRoadId, roadDic, firstRoadId, incomingRoad, cp1, linkConfig)
                nextRoadId += len(connectionRoadsForConfig)
                newConnectionRoads += connectionRoadsForConfig
            except Exception as e:
                logging.warn(f"{self.name}: {e}")
                raise e
        
        return newConnectionRoads     

    
    def createRoadsForLinkConfig(self, nextRoadId, roadDic, firstRoadId, incomingRoad, cp1, linkConfig):
        """[summary]

        Args:
            nextRoadId ([type]): [description]
            roadDic ([type]): Instead of a list of current roads, supply a dictionary where each road is keyed with its id as a string.
            firstRoadId ([type]): [description]
            incomingRoad ([type]): [description]
            cp1 ([type]): cp of the first road that is connected to the intersection.
            linkConfig ([type]): a list of tuples where each tuple defines a unique connection between two lanes. A link is a tuple ('incoming-road-id:lane-id', 'outgoing-road-id:lane-id')

        Returns:
            [type]: [description]
        """
        newConnectionRoads = []
        for link in linkConfig:
            

            fromUniqueLaneId = link[0]
            incomingLaneId = int(fromUniqueLaneId.split(':')[1])

            toUniqueLaneId = link[1]
            outgoingRoadId = int(toUniqueLaneId.split(':')[0])
            outgoingLaneId = int(toUniqueLaneId.split(':')[1])

            outgoingRoad = roadDic[outgoingRoadId]

            if firstRoadId == incomingRoad.id and firstRoadId == outgoingRoad.id: # for U-turns
                newConnection = self.createSingleLaneConnectionRoad(nextRoadId, incomingRoad, outgoingRoad, incomingLaneId, outgoingLaneId, cp1, cp1)
            elif firstRoadId == incomingRoad.id:
                newConnection = self.createSingleLaneConnectionRoad(nextRoadId, incomingRoad, outgoingRoad, incomingLaneId, outgoingLaneId, cp1, pyodrx.ContactPoint.start)
            elif firstRoadId == outgoingRoad.id:
                newConnection = self.createSingleLaneConnectionRoad(nextRoadId, incomingRoad, outgoingRoad, incomingLaneId, outgoingLaneId, pyodrx.ContactPoint.start, cp1)
            else:
                newConnection = self.createSingleLaneConnectionRoad(nextRoadId, incomingRoad, outgoingRoad, incomingLaneId, outgoingLaneId, pyodrx.ContactPoint.start, pyodrx.ContactPoint.start)

            newConnectionRoads.append(newConnection)

            nextRoadId += 1

            logging.debug(f"{self.name}: created connection for link {link}")

        return newConnectionRoads