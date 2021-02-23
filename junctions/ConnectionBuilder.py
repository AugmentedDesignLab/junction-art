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

class ConnectionBuilder:


    def __init__(self):
        self.config = Configuration()
        self.countryCode = CountryCodes.getByStr(self.config.get("countryCode"))
        self.curveBuilder = CurveRoadBuilder()
        

    
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
        
        startPos = incomingRoad.getLanePosition(incomingBoundaryId, incomingCp)
        endPos = outgoingRoad.getLanePosition(outgoingBoundaryId, outgoingCp)



        x1, y1, h1 = incomingRoad.getPosition(incomingCp)
        x2, y2, h2 = outgoingRoad.getPosition(outgoingCp)

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

        return newConnection


