import unittest, os
from junctionart.junctions.CurveRoadBuilder import CurveRoadBuilder
from scipy.interpolate import CubicHermiteSpline
from junctionart.junctions.JunctionHarvester import JunctionHarvester
import numpy as np
import pyodrx as pyodrx, extensions
from junctionart.junctions.JunctionBuilder import JunctionBuilder
from junctionart.library.Configuration import Configuration
import junctions

from junctionart.junctions.Direction import CircularDirection
from junctionart.junctions.RoadLinker import RoadLinker
from junctionart.junctions.LaneSides import LaneSides


class test_CurveRoadBuilder(unittest.TestCase):

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
        
        roads = []
        roads.append(self.curveRoadBuilder.create(0, angleBetweenEndpoints=np.pi/2, curvature=0.05,
                                                    isRightTurnLane=True))

        odrName = "test_RightTurnLaneCurve"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_RightTurnLaneCurve.xodr"
        odr.write_xml(xmlPath)
