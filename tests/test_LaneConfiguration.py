import unittest

import numpy as np
import os, dill
import pyodrx 
import extensions
from library.Configuration import Configuration
from junctions.LaneConfiguration import LaneConfigurationStrategies, LaneConfiguration
from extensions.ExtendedLaneSection import ExtendedLaneSection
from extensions.ExtendedLane import ExtendedLane


class test_LaneConfiguration(unittest.TestCase):

    def test_getLaneLinksByMergingEdge(self):

        # 1
        centerLane = ExtendedLane(pyodrx.LaneType.median)
        section1 = ExtendedLaneSection(0, centerLane)
        section2 = ExtendedLaneSection(0, centerLane)

        section1.add_left_lane(ExtendedLane(a=3))
        section1.add_right_lane(ExtendedLane(a=3))
        section2.add_left_lane(ExtendedLane(a=3))

        ls, rs = LaneConfiguration.getLaneLinksByMergingEdge(section1, section2)

        assert len(ls) == max(len(section1.leftlanes), len(section2.leftlanes))
        assert len(rs) == 0

        # [(1, 1, False)]
        assert ls[0][0] == 1 and ls[0][1] == 1 and ls[0][2] == False

        print("test 1")
        print(ls)
        print(rs)

        #2
        
        section2.add_right_lane(ExtendedLane(a=3))
        ls, rs = LaneConfiguration.getLaneLinksByMergingEdge(section1, section2)
        assert len(ls) == max(len(section1.leftlanes), len(section2.leftlanes))
        assert len(rs) == max(len(section1.rightlanes), len(section2.rightlanes))
        assert ls[0][0] == 1 and ls[0][1] == 1 and ls[0][2] == False
        assert rs[0][0] == -1 and rs[0][1] == -1 and rs[0][2] == False

        print("test 2")
        print(ls)
        print(rs)

        
        section1.add_left_lane(ExtendedLane(a=3))
        section1.add_left_lane(ExtendedLane(a=3))

        ls, rs = LaneConfiguration.getLaneLinksByMergingEdge(section1, section2)
        print("test 3")
        print(ls)
        print(rs)
        assert len(ls) == max(len(section1.leftlanes), len(section2.leftlanes))
        assert len(rs) == max(len(section1.rightlanes), len(section2.rightlanes))
        assert ls[0][0] == 1 and ls[0][1] == 1 and ls[0][2] == False
        assert rs[0][0] == -1 and rs[0][1] == -1 and rs[0][2] == False

        
        section2.add_right_lane(ExtendedLane(a=3))

        ls, rs = LaneConfiguration.getLaneLinksByMergingEdge(section1, section2)
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

        ls, rs = LaneConfiguration.getLaneLinksByMergingEdge(section1, section2)
        print("test 5")
        print(ls)
        print(rs)
        assert len(ls) == max(len(section1.leftlanes), len(section2.leftlanes))
        assert len(rs) == max(len(section1.rightlanes), len(section2.rightlanes))
        assert ls[0][0] == 1 and ls[0][1] == 1 and ls[0][2] == False
        assert rs[0][0] == -1 and rs[0][1] == -1 and rs[0][2] == False

        


