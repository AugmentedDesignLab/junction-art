import unittest, os
from junctions.CurveRoadBuilder import CurveRoadBuilder
from scipy.interpolate import CubicHermiteSpline
from junctions.JunctionHarvester import JunctionHarvester
import numpy as np
import pyodrx, extensions
from junctions.JunctionBuilder import JunctionBuilder
from library.Configuration import Configuration
import junctions

from junctions.Direction import CircularDirection
from junctions.RoadLinker import RoadLinker
from junctions.LaneSides import LaneSides


class test_StraightRoadBuilder(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()

        self.curveRoadBuilder = CurveRoadBuilder()
        self.roadLinker = RoadLinker()


    def test_SimpleCurve(self):
        
        roads = []
        roads.append(self.curveRoadBuilder.create(0, angleBetweenEndpoints=np.pi/2, curvature=0.05,
                                                    isLeftTurnLane=True))

        odrName = "test_LeftTurnLaneCurve"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_LeftTurnLaneCurve.xodr"
        odr.write_xml(xmlPath)
