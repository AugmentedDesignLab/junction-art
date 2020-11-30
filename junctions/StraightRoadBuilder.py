import numpy as np
import os
import pyodrx, extensions
import math

from junctions.LaneSides import LaneSides
from junctions.StandardCurvatures import StandardCurvature
from junctions.StandardCurveTypes import StandardCurveTypes
from extensions.ExtendedRoad import ExtendedRoad
from extensions.ExtendedPlanview import ExtendedPlanview
from scipy.interpolate import CubicHermiteSpline

from junctions.RoadSeries import RoadSeries
from junctions.Direction import CircularDirection
from junctions.Geometry import Geometry
from junctions.LaneBuilder import LaneBuilder
from extensions.CountryCodes import CountryCodes


class StraightRoadBuilder:

    def __init__(self, country = CountryCodes.US):
        self.STD_ROADMARK = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)
        self.STD_START_CLOTH = 1/1000000000
        self.country = country
        self.laneBuilder = LaneBuilder()
        pass

    
    def createStraightRoad(self, roadId, length=100,junction = -1, 
                            n_lanes=1, lane_offset=3, 
                            laneSides=LaneSides.BOTH,
                            leftTurnLane=False,
                            rightTurnLane=False):

        # create geometry
        line1 = pyodrx.Line(length)

        # create planviews
        pv = extensions.ExtendedPlanview()
        pv.add_geometry(line1)

        
        laneSections = self.laneBuilder.getStandardLanes(n_lanes, lane_offset, laneSides,
                                                            roadLength=length, leftTurnLane=leftTurnLane, rightTurnLane=rightTurnLane)


        road = ExtendedRoad(roadId, pv, laneSections, road_type=junction)
        return road


