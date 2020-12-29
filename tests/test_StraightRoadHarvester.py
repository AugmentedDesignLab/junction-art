import unittest

import numpy as np
import os, dill
import pyodrx 
import pprint
from junctions.StraightRoadHarvester import StraightRoadHarvester
from library.Configuration import Configuration
from junctions.TurnTypes import TurnTypes


class test_StraightRoadHarvester(unittest.TestCase):
    
    def setUp(self):
        
        self.configuration = Configuration()
        self.esminiPath = self.configuration.get("esminipath")
        self.harvester = StraightRoadHarvester(outputDir="./output", outputPrefix="harvest-straight-", lastId=0, esminiPath=self.esminiPath)
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
