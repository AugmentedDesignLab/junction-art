
import os
import numpy as np
import logging
from junctions.LaneSides import LaneSides
from library.Configuration import Configuration
from junctions.StraightRoadBuilder import StraightRoadBuilder
from extensions.CountryCodes import CountryCodes
from junctions.TurnTypes import TurnTypes

class StraightRoadHarvester:

    def __init__(self, 
                outputDir, 
                outputPrefix, 
                lastId=0,
                straightRoadBuilder=None,
                straightRoadLen = 2,
                esminiPath = None, 
                saveImage = True
                ):
        
        self.destinationPrefix = os.path.join(outputDir, outputPrefix)
        self.configuration = Configuration()
        self.lastId = lastId
        self.straightRoadLen = straightRoadLen

        self.straightRoadBuilder = straightRoadBuilder
        if straightRoadBuilder is None:
            self.straightRoadBuilder = StraightRoadBuilder()

        if esminiPath is None:
            self.esminiPath = self.configuration.get("esminipath")
        else:
            self.esminiPath = esminiPath

        self.saveImage = saveImage

        if os.path.isdir(self.esminiPath) is False:
            logging.warn(f"Esmini path not found {self.esminiPath}. Will break if you try to save images using harvester.")

        pass


    def harvest(self, maxLeftLanes=2, maxRightLanes=2, countryCode=CountryCodes.US, show=False):

        if countryCode != CountryCodes.US:
            raise NotImplementedError("Only US is implemented")

        # permutations
        # no merge or extension
        # each lane can have one of the 5 traffic direction.

        roads = {}

        for l in range(maxLeftLanes + 1):
            for r in range(maxRightLanes + 1):
                roads[f"{l}-{r}"] = self.harvestUS(l, r, show)
        
        # TODO save odrs
    
    def harvestUS(self, n_lanes_left=2, n_lanes_right=2, show=False):

        # incoming lanes in a junction are right lanes if end point is connected, left lanes if start point is connected.
        # 5x5x5x5 for 2, 2

        road = self.straightRoadBuilder.createWithDifferentLanes(self.lastId, length=self.straightRoadLen, n_lanes_left=n_lanes_left, n_lanes_right=n_lanes_right)

        # now iterate through lanes and set types.

        leftCombinations = self.getLaneTurnCombinations(n_lanes_left)

        rightCombinations = self.getLaneTurnCombinations(n_lanes_right)


        return None
    

    def getLaneTurnCombinations(self, n):
        """[summary]

        Args:
            n ([type]): [description]

        Returns:
            [type]: List of combinations. each combination is an ordered list
        """

        # from left to right
        if n == 1:
            return [[i] for i in TurnTypes.getAll()]

        combinations = []

        childrenCombinations = self.getLaneTurnCombinations(n-1)

        for childComb in childrenCombinations:
            possibleTurns = self.getPossibleTurnsWRTLaneOnRight(childComb[0])
            # push into child comb
            for possibleTurn in possibleTurns:
                childCopy = childComb.copy()
                childCopy.insert(0, possibleTurn)
                combinations.append(childCopy)
        
        return combinations
        

    
    def getPossibleTurnsWRTLaneOnRight(self, turnOnRight):

        if turnOnRight == TurnTypes.RIGHT:
            return TurnTypes.getAll()
        if turnOnRight in [TurnTypes.STRAIGHT_RIGHT, TurnTypes.STRAIGHT]:
            return (TurnTypes.LEFT, TurnTypes.STRAIGHT_LEFT, TurnTypes.STRAIGHT)
        
        return (TurnTypes.LEFT, ) # for ALL or LEFT types


        


