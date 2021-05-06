import unittest, os
from junctions.RotatedStraightRoadBuilder import RotatedStraightRoadBuilder
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
from junctions.CurveRoadBuilder import CurveRoadBuilder
from extensions.CountryCodes import CountryCodes
from junctions.StandardCurveTypes import StandardCurveTypes


class test_RotatedStraightRoadBuilder(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()

        self.rotatedStraightRoadBuilder = RotatedStraightRoadBuilder()
        self.curveBuilder = CurveRoadBuilder(country=CountryCodes.US)
        self.roadLinker = RoadLinker()

    def test_createRoadWithAngle(self):
        
        roads = []
        roads.append(self.rotatedStraightRoadBuilder.createRoadWithAngle(road_id=0, x=0.0, y=0.0, angle=np.pi/4, length=30))
        
        secondConnectionRoad = self.curveBuilder.create(roadId=1, angleBetweenEndpoints=-np.pi/4, curveType=StandardCurveTypes.LongArc)
        roads.append(secondConnectionRoad)
        roads[0].addExtendedSuccessor(road=secondConnectionRoad, angleWithRoad=0, cp=pyodrx.ContactPoint.start)
        secondConnectionRoad.addExtendedPredecessor(road=roads[0], angleWithRoad=0, cp=pyodrx.ContactPoint.end)

        odrName = "test_rotated straight road"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        # xmlPath = f"output/test-LeftTurnLane.xodr"
        # odr.write_xml(xmlPath)