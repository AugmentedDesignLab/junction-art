import unittest, os, math
from junctionart.junctions.StraightRoadBuilder import StraightRoadBuilder
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
from junctionart.junctions.StandardCurveTypes import StandardCurveTypes
from junctionart.junctions.ConnectionBuilder import ConnectionBuilder
from junctionart.junctions.CurveRoadBuilder import CurveRoadBuilder


class test_ExtendedRoad(unittest.TestCase):
    def setUp(self):
        
        self.configuration = Configuration()
        self.esminipath = self.configuration.get("esminipath")
        self.roadBuilder = junctions.RoadBuilder()

        self.straightRoadBuilder = StraightRoadBuilder()
        self.roadLinker = RoadLinker()
        self.connectionBuilder = ConnectionBuilder()
        self.curveRoadBuilder = CurveRoadBuilder()

    
    def test_createSingleLaneConnectionRoad(self):
        

        roads = []

        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=10, junction=-1, n_lanes_left=2, n_lanes_right=2))
        roads.append(self.curveRoadBuilder.createSimple(1, np.pi/3, isJunction=True, n_lanes=2))
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=2, n_lanes_right=2))
        
        RoadLinker.createExtendedPredSuc(predRoad=roads[0], predCp=pyodrx.ContactPoint.end, sucRoad=roads[1], sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=roads[1], predCp=pyodrx.ContactPoint.end, sucRoad=roads[2], sucCP=pyodrx.ContactPoint.start)

        odrName = "test_createSingleLaneConnectionRoad"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        # extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        newConnection = self.connectionBuilder.createSingleLaneConnectionRoad(3, roads[0], roads[2], -2, -2, pyodrx.ContactPoint.end, pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=roads[0], predCp=pyodrx.ContactPoint.end, sucRoad=newConnection, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=newConnection, predCp=pyodrx.ContactPoint.end, sucRoad=roads[2], sucCP=pyodrx.ContactPoint.start)
        newConnection.updatePredecessorOffset(-1)

        roads.append(newConnection)
        odr.add_road(newConnection)

        newConnection = self.connectionBuilder.createSingleLaneConnectionRoad(4, roads[2], roads[0], 2, 2, pyodrx.ContactPoint.start, pyodrx.ContactPoint.end)
        RoadLinker.createExtendedPredSuc(predRoad=roads[2], predCp=pyodrx.ContactPoint.start, sucRoad=newConnection, sucCP=pyodrx.ContactPoint.start)
        RoadLinker.createExtendedPredSuc(predRoad=newConnection, predCp=pyodrx.ContactPoint.end, sucRoad=roads[0], sucCP=pyodrx.ContactPoint.end)
        newConnection.updatePredecessorOffset(1)

        

        roads.append(newConnection)
        odr.add_road(newConnection)
        
        odr.resetAndReadjust(byPredecessor=True)
        extensions.printRoadPositions(odr)
        
        extensions.view_road(odr, os.path.join('..', self.esminipath))
        xmlPath = f"output/test_createSingleLaneConnectionRoad.xodr"
        odr.write_xml(xmlPath)

