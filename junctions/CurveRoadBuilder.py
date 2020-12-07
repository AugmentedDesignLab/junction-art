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


class CurveRoadBuilder:

    def __init__(self, country = CountryCodes.US):
        self.STD_ROADMARK = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)
        self.STD_START_CLOTH = 1/1000000000
        self.country = country
        self.laneBuilder = LaneBuilder()
        pass
