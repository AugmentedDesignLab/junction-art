from junctionart.extensions.ExtendedLane import ExtendedLane
from junctionart.junctions.Geometry import Geometry
from junctionart.junctions.LaneSides import LaneSides
from junctionart.roundabout.LogFlow import LogFlow
from junctionart.roundabout.RewardUtil import RewardUtil
from junctionart.roundabout.RoundaboutLaneEncodingEnv import RoundaboutLaneEncodingEnv
import pyodrx as pyodrx
from junctionart.extensions.CountryCodes import CountryCodes
import unittest
from junctionart.library.Configuration import Configuration
import junctionart.extensions as extensions, os
import math
from junctionart.roundabout.ClassicGenerator import ClassicGenerator
from junctionart.junctions.JunctionBuilder import JunctionBuilder
from junctionart.junctions.LaneBuilder import LaneBuilder
from junctionart.junctions.CurveRoadBuilder import CurveRoadBuilder
from junctionart.junctions.StandardCurvatures import StandardCurvature
from junctionart.junctions.RoadBuilder import RoadBuilder
from junctionart.junctions.StraightRoadBuilder import StraightRoadBuilder
from junctionart.junctions.RoadLinker import RoadLinker
from junctionart.junctions.ODRHelper import ODRHelper
import numpy as np
import random
import pickle
from pyodrx.lane import LaneSection
import sys

class test_EncodingEnv(unittest.TestCase):
    def setUp(self):
        self.builder = RoundaboutLaneEncodingEnv(country=CountryCodes.US, laneWidth=3)

    def test_createRoundAboutFromIncidentPoints1(self):

        threePoints = [
            {"x": 80, "y": 20, "heading": math.radians(45),'leftLane': 2, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            {"x": 210, "y": 20, "heading": math.radians(115),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            {"x": 100, "y": 90, "heading": math.radians(300),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            # {"x": 160, "y": 49, "heading": math.radians(300),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
            # {"x": 160, "y": 100, "heading": math.radians(220),'leftLane': 1, 'rightLane': 1, 'medianType': None, 'skipEndpoint': None},
        ]
        self.builder.generateWithRoadDefinition(
            threePoints,
            outgoingLanesMerge=False,
            nSegments=10,
            laneToCircularId=[9, 10, 6, 4, 1, 7, 4]
        )
        roundabout = self.builder.getRoundabout()
        print(RewardUtil.score(roundabout))
        roundabout.showRoundabout()

    def test_gflow(self):
        layers = [15, 128, 256, 15]
        nSlots = 5
        lgF = LogFlow(layers=layers, nSlots=nSlots)

        laneToCircularIDs=[-1, 1, -1]
        state = RewardUtil.encodeState(laneToCircularIDs, nSlots)
        newState = lgF.forward(state)
        print(newState)

    