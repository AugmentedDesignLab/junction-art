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

from library.Configuration import Configuration

from junctions.StraightRoadBuilder import StraightRoadBuilder

class RotatedStraightRoadBuilder(StraightRoadBuilder):
    def __init__(self):
        super().__init__()

        pass


    def createRoadWithAngle(self, road_id=0, x=0, y=0, angle=np.pi/6, length=10):
        pv = self.createPVForLine(length)
        geom = pv._raw_geometries
        pv.set_start_point(x_start=x, y_start=y, h_start=angle)


        laneSections = self.laneBuilder.getLanes(n_lanes_left=1, n_lanes_right=1)

        road = ExtendedRoad(road_id=road_id, planview=pv, lanes=laneSections) 

        return road
