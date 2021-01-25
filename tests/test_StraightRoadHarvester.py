import unittest

import numpy as np
import os, dill
import pyodrx 
import pprint
from junctions.StraightRoadHarvester import StraightRoadHarvester
from junctions.StraightRoadBuilder import StraightRoadBuilder
from library.Configuration import Configuration
from junctions.TurnTypes import TurnTypes
from extensions.CountryCodes import CountryCodes


class test_StraightRoadHarvester(unittest.TestCase):
    
    def setUp(self):
        
        self.configuration = Configuration()
        self.esminiPath = self.configuration.get("esminipath")
        self.harvester = StraightRoadHarvester(outputDir="./output", outputPrefix="harvest-straight-", lastId=0, straightRoadLen=5, esminiPath=self.esminiPath)
        self.straightRoadBuilder = StraightRoadBuilder()
        self.pp = pprint.PrettyPrinter(indent=4)

    
    def test_getPossibleTurnsWRTLaneOnRight(self):
        possibleTurns = self.harvester.getPossibleTurnsWRTLaneOnRight(TurnTypes.RIGHT)
        assert len(possibleTurns) == 6

        possibleTurns = self.harvester.getPossibleTurnsWRTLaneOnRight(TurnTypes.STRAIGHT_RIGHT)
        assert len(possibleTurns) == 3

        possibleTurns = self.harvester.getPossibleTurnsWRTLaneOnRight(TurnTypes.STRAIGHT)
        print(possibleTurns)
        assert len(possibleTurns) == 3

        possibleTurns = self.harvester.getPossibleTurnsWRTLaneOnRight(TurnTypes.STRAIGHT_LEFT)
        print(possibleTurns)
        assert len(possibleTurns) == 1
        possibleTurns = self.harvester.getPossibleTurnsWRTLaneOnRight(TurnTypes.LEFT)
        print(possibleTurns)
        assert len(possibleTurns) == 1
        possibleTurns = self.harvester.getPossibleTurnsWRTLaneOnRight(TurnTypes.ALL)
        print(possibleTurns)
        assert len(possibleTurns) == 1
    

    def test_getLaneTurnCombinations(self):

        combinations = self.harvester.getLaneTurnCombinations(1)
        # self.pp.pprint(combinations)
        assert len(combinations) == 6

        combinations = self.harvester.getLaneTurnCombinations(2)
        self.pp.pprint(combinations)
        print(len(combinations))
        assert len(combinations) == 15

    
    def test_applyTurnCombinationOnLanes(self):
        
        road = self.straightRoadBuilder.createWithDifferentLanes(0, length=10, n_lanes_left=2, n_lanes_right=2)
        leftCombinations = self.harvester.getLaneTurnCombinations(2)
        rightCombinations = leftCombinations

        laneSectionForLeft = road.getFirstLaneSection()
        laneSectionForRight = road.getLastLaneSection()

        self.harvester.applyTurnCombinationOnLanes(laneSectionForLeft.leftlanes, leftCombinations[0])

        self.harvester.applyTurnCombinationOnLanes(laneSectionForRight.rightlanes, rightCombinations[0])

        assert laneSectionForLeft.leftlanes[0].turnType == leftCombinations[0][0]
        assert laneSectionForLeft.leftlanes[0].turnType == rightCombinations[0][0]

    
    def test_harvestUS(self):

        odrs = self.harvester.harvestUS(2, 2, False)

        print(len(odrs))

    
    def test_harvest(self):
        self.harvester.harvest(maxLeftLanes=2, maxRightLanes=2, countryCode=CountryCodes.US)
