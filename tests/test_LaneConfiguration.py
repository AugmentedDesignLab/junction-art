import unittest

import numpy as np
import os, dill
import pyodrx 
import extensions
from library.Configuration import Configuration
from junctions.LaneConfiguration import LaneConfigurationStrategies, LaneConfiguration
from extensions.ExtendedLaneSection import ExtendedLaneSection
from extensions.ExtendedLane import ExtendedLane
from junctions.StraightRoadBuilder import StraightRoadBuilder
from extensions.CountryCodes import CountryCodes


class test_LaneConfiguration(unittest.TestCase):

    def setUp(self):
        
        self.configuration = Configuration()

        self.straightRoadBuilder = StraightRoadBuilder()


    def test_getLaneLinksByMergingEdge(self):

        # 1
        centerLane = ExtendedLane(pyodrx.LaneType.median)
        section1 = ExtendedLaneSection(0, centerLane)
        section2 = ExtendedLaneSection(0, centerLane)

        section1.add_left_lane(ExtendedLane(a=3))
        section1.add_right_lane(ExtendedLane(a=3))

        section2.add_left_lane(ExtendedLane(a=3))

        ls, rs = LaneConfiguration.getLaneLinksByMergingEdge(section1, section2, False)

        assert len(ls) == max(len(section1.leftlanes), len(section2.leftlanes))
        assert len(rs) == 0

        # [(1, 1, False)]
        assert ls[0][0] == 1 and ls[0][1] == 1 and ls[0][2] == False

        print("test 1")
        print(ls)
        print(rs)

        #2
        
        section2.add_right_lane(ExtendedLane(a=3))
        ls, rs = LaneConfiguration.getLaneLinksByMergingEdge(section1, section2, False)
        assert len(ls) == max(len(section1.leftlanes), len(section2.leftlanes))
        assert len(rs) == max(len(section1.rightlanes), len(section2.rightlanes))
        assert ls[0][0] == 1 and ls[0][1] == 1 and ls[0][2] == False
        assert rs[0][0] == -1 and rs[0][1] == -1 and rs[0][2] == False

        print("test 2")
        print(ls)
        print(rs)

        
        section1.add_left_lane(ExtendedLane(a=3))
        section1.add_left_lane(ExtendedLane(a=3))

        ls, rs = LaneConfiguration.getLaneLinksByMergingEdge(section1, section2, False)
        print("test 3")
        print(ls)
        print(rs)
        assert len(ls) == max(len(section1.leftlanes), len(section2.leftlanes))
        assert len(rs) == max(len(section1.rightlanes), len(section2.rightlanes))
        assert ls[0][0] == 1 and ls[0][1] == 1 and ls[0][2] == False
        assert rs[0][0] == -1 and rs[0][1] == -1 and rs[0][2] == False

        
        section2.add_right_lane(ExtendedLane(a=3))

        ls, rs = LaneConfiguration.getLaneLinksByMergingEdge(section1, section2, False)
        print("test 4")
        print(ls)
        print(rs)
        assert len(ls) == max(len(section1.leftlanes), len(section2.leftlanes))
        assert len(rs) == max(len(section1.rightlanes), len(section2.rightlanes))
        assert ls[0][0] == 1 and ls[0][1] == 1 and ls[0][2] == False
        assert rs[0][0] == -1 and rs[0][1] == -1 and rs[0][2] == False

        
        section2.add_left_lane(ExtendedLane(a=3))
        section2.add_left_lane(ExtendedLane(a=3))
        section2.add_left_lane(ExtendedLane(a=3))
        section2.add_left_lane(ExtendedLane(a=3))
        section1.add_right_lane(ExtendedLane(a=3))
        section1.add_right_lane(ExtendedLane(a=3))

        ls, rs = LaneConfiguration.getLaneLinksByMergingEdge(section1, section2, False)
        print("test 5")
        print(ls)
        print(rs)
        assert len(ls) == max(len(section1.leftlanes), len(section2.leftlanes))
        assert len(rs) == max(len(section1.rightlanes), len(section2.rightlanes))
        assert ls[0][0] == 1 and ls[0][1] == 1 and ls[0][2] == False
        assert rs[0][0] == -1 and rs[0][1] == -1 and rs[0][2] == False

        
        straightLanesLeft = set([i for i, _, conType in ls if conType == 0])
        print(straightLanesLeft)

        


    def test_getIntersectionLinks1ToMany(self):

        incomingLanes = ['1:-1', '1:-2']
        outgoingLanes = ['2:1']

        try:
            LaneConfiguration.getIntersectionLinks1ToMany(incomingLanes, outgoingLanes)
            assert False
        except Exception as e:
            print(e)
            pass

        incomingLanes = ['1:-1', '1:-2']
        outgoingLanes = ['2:1', '2:2']

        try:
            connections = LaneConfiguration.getIntersectionLinks1ToMany(incomingLanes, outgoingLanes)
            assert connections[0][0] == '1:-1'
            assert connections[0][1] == '2:1'
            assert connections[0][2] == 0
            assert connections[1][0] == '1:-2'
            assert connections[1][1] == '2:2'
            assert connections[1][2] == 0
            # print(connections)
        except Exception as e:
            print(e)
            assert False


        incomingLanes = ['1:-1', '1:-2']
        outgoingLanes = ['2:1', '2:2', '3:1']

        try:
            connections = LaneConfiguration.getIntersectionLinks1ToMany(incomingLanes, outgoingLanes)
            assert connections[0][0] == '1:-1'
            assert connections[0][1] == '2:1'
            assert connections[0][2] == 0
            assert connections[1][0] == '1:-2'
            assert connections[1][1] == '2:2'
            assert connections[1][2] == 0
            assert connections[2][0] == '1:-2'
            assert connections[2][1] == '3:1'
            assert connections[2][2] == 2
            print(connections)
        except Exception as e:
            print(e)
            assert False


    def test_getUniqueLaneIds(self):

        roads = []
        roads.append(self.straightRoadBuilder.create(0, length = 10, n_lanes=2))
        laneIds = LaneConfiguration.getUniqueLaneIds(roads[0], roads[0].getLaneSectionByCP(pyodrx.ContactPoint.start).leftlanes)
        # print(laneIds)
        assert laneIds[0] == '0:1'
        assert laneIds[1] == '0:2'

        laneIds = LaneConfiguration.getUniqueLaneIds(roads[0], roads[0].getLaneSectionByCP(pyodrx.ContactPoint.start).rightlanes)
        assert laneIds[0] == '0:-1'
        assert laneIds[1] == '0:-2'

    

    def test_getOutgoingLanesFromARoad(self):
        
        roads = []
        roads.append(self.straightRoadBuilder.create(0, length = 10, n_lanes=2))
        roads.append(self.straightRoadBuilder.create(1, length = 10, n_lanes=1))
        roads.append(self.straightRoadBuilder.create(2, length = 10, n_lanes=2))

        inLanes = LaneConfiguration.getIncomingLaneIdsOnARoad(roads[0], pyodrx.ContactPoint.end, CountryCodes.US)
        outLanes = LaneConfiguration.getOutgoingLanesIdsFromARoad(roads[0], roads, cp1=pyodrx.ContactPoint.end, countryCode=CountryCodes.US)
        assert inLanes[0] == '0:-1'
        assert inLanes[1] == '0:-2'
        assert outLanes[0] == '1:-1'
        assert outLanes[1] == '2:-1'
        assert outLanes[2] == '2:-2'


        inLanes = LaneConfiguration.getIncomingLaneIdsOnARoad(roads[2], pyodrx.ContactPoint.start, CountryCodes.US)
        outLanes = LaneConfiguration.getOutgoingLanesIdsFromARoad(roads[2], roads, cp1=pyodrx.ContactPoint.end, countryCode=CountryCodes.US)
        print(inLanes)
        print(outLanes)
        assert inLanes[0] == '2:1'
        assert inLanes[1] == '2:2'
        assert outLanes[0] == '0:1'
        assert outLanes[1] == '0:2'
        assert outLanes[2] == '1:-1'

        linkConfig = LaneConfiguration.getIntersectionLinks1ToMany(inLanes, outLanes)

        print(linkConfig)
