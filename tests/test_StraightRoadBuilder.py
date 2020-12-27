import unittest, os
from junctions.StraightRoadBuilder import StraightRoadBuilder
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

        self.straightRoadBuilder = StraightRoadBuilder()
        self.roadLinker = RoadLinker()

    

    def test_LeftTurnLanes(self):
        
        roads = []
        roads.append(self.straightRoadBuilder.create(0, length = 10, isLeftTurnLane=True))

        odrName = "test_LeftTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-LeftTurnLane.xodr"
        odr.write_xml(xmlPath)

    def test_RightTurnLanes(self):
        
        roads = []
        roads.append(self.straightRoadBuilder.create(0, length = 10, isRightTurnLane=True))

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-RightTurnLane.xodr"
        odr.write_xml(xmlPath)


    def test_TurnLanes(self):
        
        roads = []
        roads.append(self.straightRoadBuilder.create(0, length = 10, isRightTurnLane=True, isLeftTurnLane=True))
        roads.append(self.straightRoadBuilder.create(1, length = 10, n_lanes=2))

        
        RoadLinker.createExtendedPredSuc(predRoad=roads[0], predCp=pyodrx.ContactPoint.end, sucRoad=roads[1], sucCP=pyodrx.ContactPoint.start)

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-TurnLanes.xodr"
        odr.write_xml(xmlPath)


    def test_MergeLanes(self):
        
        roads = []
        roads.append(self.straightRoadBuilder.create(0, length = 10, isLeftMergeLane=True))

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-LeftMergeLane.xodr"
        odr.write_xml(xmlPath)

        roads = []
        roads.append(self.straightRoadBuilder.create(0, length = 10, isRightMergeLane=True))

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-RightMergeLanes.xodr"
        odr.write_xml(xmlPath)

        roads = []
        roads.append(self.straightRoadBuilder.create(0, length = 10, n_lanes=2))
        roads.append(self.straightRoadBuilder.create(1, length = 10, isLeftMergeLane=True, isRightMergeLane=True))

        RoadLinker.createExtendedPredSuc(predRoad=roads[0], predCp=pyodrx.ContactPoint.end, sucRoad=roads[1], sucCP=pyodrx.ContactPoint.start)



        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-MergeLanes.xodr"
        odr.write_xml(xmlPath)


    def test_mergeAndTurns(self):

        roads = []
        roads.append(self.straightRoadBuilder.create(0, length = 10, n_lanes=2))
        roads.append(self.straightRoadBuilder.create(1, length = 10, isLeftMergeLane=True, isRightMergeLane=True))
        roads.append(self.straightRoadBuilder.create(2, length = 10))
        roads.append(self.straightRoadBuilder.create(3, length = 10, isRightTurnLane=True, isLeftTurnLane=True))
        roads.append(self.straightRoadBuilder.create(4, length = 10, n_lanes=2))

        self.roadLinker.linkConsecutiveRoadsWithNoBranches(roads)
        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test-MergeAndTurns.xodr"
        odr.write_xml(xmlPath)



    def test_LeftTurnLaneOnRightShiftingLeftSide(self):
        roads = []
        roads.append(self.straightRoadBuilder.create(0, length = 10, laneSides=LaneSides.RIGHT,
                                                                     isLeftTurnLane=True))

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_LeftTurnLaneOnRight.xodr"
        odr.write_xml(xmlPath)



    def test_RightTurnLaneOnLeft(self):
        roads = []
        roads.append(self.straightRoadBuilder.create(0, length = 10, laneSides=LaneSides.LEFT,
                                                                     isRightTurnLane=True))

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_RightTurnLaneOnLeft.xodr"
        odr.write_xml(xmlPath)


    def test_createStraightRoadWithLeftTurnLanesOnRight(self):
        roads = []

        roads.append(self.straightRoadBuilder.createWithLeftTurnLanesOnRight(1, length = 10, n_lanes=0, 
                                                                                        numberOfLeftTurnLanesOnRight=2))
        self.roadLinker.linkConsecutiveRoadsWithNoBranches(roads)

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_createStraightRoadWithLeftTurnLanesOnRight1.xodr"
        odr.write_xml(xmlPath)



        roads = []

        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=10, junction=-1, n_lanes_left=3, n_lanes_right=1))
        roads.append(self.straightRoadBuilder.createWithLeftTurnLanesOnRight(1, length = 10, n_lanes=1, 
                                                                                        isLeftTurnLane=True, 
                                                                                        isRightTurnLane=True,
                                                                                        numberOfLeftTurnLanesOnRight=2))
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=2, n_lanes_right=4))
        self.roadLinker.linkConsecutiveRoadsWithNoBranches(roads)

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_createStraightRoadWithLeftTurnLanesOnRight2.xodr"
        odr.write_xml(xmlPath)


    def test_createStraightRoadWithRightTurnLanesOnLeft(self):
        roads = []

        roads.append(self.straightRoadBuilder.createWithRightTurnLanesOnLeft(1, length = 10, n_lanes=0, 
                                                                                        numberOfRightTurnLanesOnLeft=2))
        self.roadLinker.linkConsecutiveRoadsWithNoBranches(roads)

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_createStraightRoadWithRightTurnLanesOnLeft1.xodr"
        odr.write_xml(xmlPath)



        roads = []

        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=10, junction=-1, n_lanes_left=1, n_lanes_right=3))
        roads.append(self.straightRoadBuilder.createWithRightTurnLanesOnLeft(1, length = 10, n_lanes=1, 
                                                                                        isLeftTurnLane=True, 
                                                                                        isRightTurnLane=True,
                                                                                        numberOfRightTurnLanesOnLeft=2))
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=4, n_lanes_right=2))
        self.roadLinker.linkConsecutiveRoadsWithNoBranches(roads)

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_createStraightRoadWithRightTurnLanesOnLeft2.xodr"
        odr.write_xml(xmlPath)



    def test_createStraightRoadWithInternalTurnLanes(self):
 
        self.test_createStraightRoadWithRightTurnLanesOnLeft()
        self.test_createStraightRoadWithLeftTurnLanesOnRight()

    
    def test_createStraightRoadWithInternalTurnLanesWithoutMergeOnTheOppositeSide(self):
        roads = []

        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=10, junction=-1, n_lanes_left=1, n_lanes_right=2))
        roads.append(self.straightRoadBuilder.createWithRightTurnLanesOnLeft(1, length = 10, n_lanes=1, 
                                                                                        isLeftTurnLane=True, 
                                                                                        isRightTurnLane=True,
                                                                                        numberOfRightTurnLanesOnLeft=2,
                                                                                        mergeLaneOnTheOppositeSideForInternalTurn=False))
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=4, n_lanes_right=2))
        self.roadLinker.linkConsecutiveRoadsWithNoBranches(roads)

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_createStraightRoadWithRightTurnLanesOnLeftWithoutMergeOnTheOppositeSide.xodr"
        odr.write_xml(xmlPath)

        


        roads = []

        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=10, junction=-1, n_lanes_left=2, n_lanes_right=1))
        roads.append(self.straightRoadBuilder.createWithLeftTurnLanesOnRight(1, length = 10, n_lanes=1, 
                                                                                        isLeftTurnLane=True, 
                                                                                        isRightTurnLane=True,
                                                                                        numberOfLeftTurnLanesOnRight=2,
                                                                                        mergeLaneOnTheOppositeSideForInternalTurn=False))
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=2, n_lanes_right=4))
        self.roadLinker.linkConsecutiveRoadsWithNoBranches(roads)

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_createStraightRoadWithLeftTurnLanesOnRightWithoutMergeOnTheOppositeSide.xodr"
        odr.write_xml(xmlPath)

    

    def test_SingleSide(self):


        roads = []

        roads.append(self.straightRoadBuilder.createWithDifferentLanes(0, length=10, junction=-1, n_lanes_left=0, n_lanes_right=1))
        roads.append(self.straightRoadBuilder.createWithSingleSide(1, length = 10, n_lanes=1, 
                                                                    laneSide=LaneSides.RIGHT,
                                                                    isLeftTurnLane=True, 
                                                                    isRightTurnLane=True))
        roads.append(self.straightRoadBuilder.createWithDifferentLanes(2, length=10, junction=-1, n_lanes_left=0, n_lanes_right=3))
        self.roadLinker.linkConsecutiveRoadsWithNoBranches(roads)

        odrName = "test_RightTurnLane"
        odr = extensions.createOdrByPredecessor(odrName, roads, [])
        
        extensions.view_road(odr, os.path.join('..', self.configuration.get("esminipath")))

        xmlPath = f"output/test_createStraightSingleSide.xodr"
        odr.write_xml(xmlPath)

