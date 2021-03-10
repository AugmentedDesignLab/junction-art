import pyodrx
import extensions
import math
import numpy as np
from library.Configuration import Configuration
from extensions.CountryCodes import CountryCodes
from junctions.CurveRoadBuilder import CurveRoadBuilder
from junctions.Geometry import Geometry
from scipy.interpolate import CubicHermiteSpline
from junctions.LaneSides import LaneSides
from junctions.RoadLinker import RoadLinker
from junctions.LaneConfiguration import LaneConfiguration
import logging

class ConnectionBuilder:


    def __init__(self):
        self.config = Configuration()
        self.countryCode = CountryCodes.getByStr(self.config.get("countryCode"))
        self.curveBuilder = CurveRoadBuilder()
        self.name = "ConnectionBuilder"
        

    
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
        if self.countryCode == CountryCodes.US:
            laneSides = LaneSides.RIGHT
        if self.countryCode == CountryCodes.UK:
            laneSides = LaneSides.LEFT
        
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

        print("start: ", x1, y1, h1)
        print("end: ", x2, y2, h2)

        xCoeffs, yCoeffs = Geometry.getCoeffsForParamPoly(x1, y1, h1, x2, y2, h2, incomingCp, outgoingCp)

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

        return newConnection


    def createSingleLaneConnectionRoads(self, nextRoadId, outsideRoads, cp1):
        """Assumes all roads are connected by start point except for the first one

        Args:
            outsideRoads ([type]): [description]
            cp1 ([type]): [description]

        Returns:
            [type]: [description]
        """

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
                linkConfig = LaneConfiguration.getIntersectionLinks1ToMany(incomingLaneIds, outgoingLaneIds)

                # for each link, create a new connection road
                for link in linkConfig:

                    fromUniqueLaneId = link[0]
                    incomingLaneId = int(fromUniqueLaneId.split(':')[1])

                    toUniqueLaneId = link[1]
                    outgoingRoadId = int(toUniqueLaneId.split(':')[0])
                    outgoingLaneId = int(toUniqueLaneId.split(':')[1])

                    outgoingRoad = roadDic[outgoingRoadId]

                    if firstRoadId == incomingRoad.id:
                        newConnection = self.createSingleLaneConnectionRoad(nextRoadId, incomingRoad, outgoingRoad, incomingLaneId, outgoingLaneId, cp1, pyodrx.ContactPoint.start)
                    elif firstRoadId == outgoingRoad.id:
                        newConnection = self.createSingleLaneConnectionRoad(nextRoadId, incomingRoad, outgoingRoad, incomingLaneId, outgoingLaneId, pyodrx.ContactPoint.start, cp1)
                    else:
                        newConnection = self.createSingleLaneConnectionRoad(nextRoadId, incomingRoad, outgoingRoad, incomingLaneId, outgoingLaneId, pyodrx.ContactPoint.start, pyodrx.ContactPoint.start)

                    newConnectionRoads.append(newConnection)

                    nextRoadId += 1

                    logging.info(f"{self.name}: created connection for link {link}")
            except Exception as e:
                logging.warn(f"{self.name}: {e}")
            break
            

        return newConnectionRoads     
