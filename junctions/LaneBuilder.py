import pyodrx
import junctions
import extensions
import math
from junctions.LaneSides import LaneSides
from extensions.LaneOffset import LaneOffset
from junctions.TurnTypes import TurnTypes
from extensions.ExtendedLane import ExtendedLane
from junctions.LaneConfiguration import LaneConfigurationStrategies, LaneConfiguration
from extensions.ExtendedRoad import ExtendedRoad

from junctions.RoadLinker import RoadLinker

from library.Configuration import Configuration


class LaneBuilder:


    def __init__(self):
        self.config = Configuration()
        self.defaultLaneWidth = self.config.get("default_lane_width")

    def getStandardLanes(self, n_lanes, lane_offset, laneSides=LaneSides.BOTH,
                            roadLength = None,
                            isLeftTurnLane=False,
                            isRightTurnLane=False,
                            isLeftMergeLane=False,
                            isRightMergeLane=False):
        """[summary] Don't allow both merge lanes and turn lanes in a road. Better split to two roads
        TODO allow merge and turn in opposite sides of a road

        Args:
            n_lanes ([type]): [description]
            lane_offset ([type]): width
            laneSides ([type], optional): where to put lanes wrt center lane. Defaults to LaneSides.BOTH.

        Returns:
            ExtenndedLanes: Road with one lane section if there is no merge or turn lanes. 3 sections otherwise. 
                            In case of turns, the first section will have no turn lanes. In case of merges, the last section will have no merge lanes.
                            In case of a single side, all the turns or merge will be added on the single side only. Otherside will have no lanes
        """
        if laneSides != LaneSides.BOTH:
            return self.getStandardTurnsOnSingleSide(n_lanes, lane_offset, laneSides,
                                            roadLength=roadLength, 
                                            isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
                                            isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane
                                        )
        elif self.anyTurnOrMerge(isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane):
            return self.getStandardLanesWithInternalTurns(n_lanes, lane_offset, laneSides,
                                                                roadLength=roadLength, 
                                                                isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
                                                                isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane,
                                                                )
        else:
            return self.getStandardLanesWithDifferentLeftAndRight(n_lanes, n_lanes, lane_offset)                                

    def anyTurnOrMerge(self, isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane):
        return isLeftTurnLane or isRightTurnLane or isLeftMergeLane or isRightMergeLane


    def getStandardLanesWithDifferentLeftAndRight(self,
                            n_lanes_left, n_lanes_right,
                            lane_offset,
                            singleSide=False
                            ):
        """[summary]

        Args:
            n_lanes_left ([type]): [description]
            n_lanes_right ([type]): [description]
            lane_offset ([type]): [description]

        Returns:
            ExtendedLanes : An extended lanes object with 3 lane sections.
        """
                            

        firstSec = self.getStandardLaneSection(0, n_lanes_left, n_lanes_right, lane_offset, singleSide=singleSide)
        laneSections = extensions.ExtendedLanes()
        laneSections.add_lanesection(firstSec)
        return laneSections


    def getStandardTurnsOnSingleSide(self, n_lanes, lane_offset, laneSide=LaneSides.RIGHT,
                            roadLength = None,
                            isLeftTurnLane=False,
                            isRightTurnLane=False,
                            isLeftMergeLane=False,
                            isRightMergeLane=False,
                            laneOffset = 0):
        """[summary] Don't allow both merge lanes and turn lanes in a road. Better split to two roads
        TODO allow merge and turn in opposite sides of a road

        Args:
            n_lanes ([type]): [description]
            lane_offset ([type]): width
            laneSides ([type], optional): where to put lanes wrt center lane. Defaults to LaneSides.RIGHT.

        Returns:
            [type]: Road with one lane section if there is no merge or turn lanes. 3 sections otherwise. 
            In case of turns, the first section will have no turn lanes. In case of merges, the last section will have no merge lanes.
            One side will have no lanes.
        """

        if laneSide == LaneSides.BOTH:
            raise Exception(f"Lanes side can be left or right only.")

        self.checkTurnAndMergeConflict(isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane)

        self.checkRoadLengthRequirement(isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane, roadLength)


        
        n_lanes_left = 0
        n_lanes_right = 0

        if laneSide == LaneSides.RIGHT:
            n_lanes_right = n_lanes
        else:
            n_lanes_left = n_lanes

        firstSec = self.getStandardLaneSection(0, n_lanes_left, n_lanes_right, lane_offset=lane_offset, singleSide=True)
        extendedLanes = extensions.ExtendedLanes()
        extendedLanes.add_lanesection(firstSec)

        if self.anyTurnOrMerge(isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane):

            turnOffSet, finalOffset, curveLaneLength = self.getOffsetsAndTurnLaneCurveLength(roadLength) 
            midSecWithTurns = self.getStandardLaneSection(turnOffSet, n_lanes_left, n_lanes_right, lane_offset=lane_offset, singleSide=True)
            finalSection = self.getStandardLaneSection(finalOffset, n_lanes_left, n_lanes_right, lane_offset=lane_offset, singleSide=True)

            

            # 1 add the turn Section
            # 2 final section should have no turns.

            turnLaneOffset = None
            finalLaneOffset = None

            if laneSide == LaneSides.RIGHT:
                if isLeftTurnLane:
                    # we need to change the center lane offset for mid and final

                    lane = self.createLinearTurnLane(TurnTypes.LEFT, lane_offset, curveLaneLength)
                    midSecWithTurns.prependLaneToRightLanes(lane)
                    finalSection.prependLaneToRightLanes(pyodrx.standard_lane(lane_offset))

                    # now the offsets
                    # 1. one for turnOffset
                    # 2. one for finalOffset
                    turnLaneOffset = LaneOffset.createLinear(turnOffSet, maxWidth=lane_offset, laneLength=curveLaneLength)
                    finalLaneOffset = LaneOffset.createParallel(finalOffset, a=lane_offset)
                if isRightTurnLane:
                    lane = self.createLinearTurnLane(TurnTypes.RIGHT, lane_offset, curveLaneLength)
                    midSecWithTurns.add_right_lane(lane)
                    finalSection.add_right_lane(pyodrx.standard_lane(lane_offset))
            
            if laneSide == LaneSides.LEFT:
                if isLeftTurnLane:
                    lane = self.createLinearTurnLane(TurnTypes.LEFT, lane_offset, curveLaneLength)
                    midSecWithTurns.add_left_lane(lane)
                    finalSection.add_left_lane(pyodrx.standard_lane(lane_offset))

                if isRightTurnLane:
                    # we need to change the center lane offset for mid and final

                    lane = self.createLinearTurnLane(TurnTypes.RIGHT, lane_offset, curveLaneLength)
                    midSecWithTurns.prependLaneToLeftLanes(lane)
                    finalSection.prependLaneToLeftLanes(pyodrx.standard_lane(lane_offset))

                    # now the offsets
                    # 1. one for turnOffset
                    # 2. one for finalOffset
                    turnLaneOffset = LaneOffset.createLinear(turnOffSet, maxWidth=-lane_offset, laneLength=curveLaneLength)
                    finalLaneOffset = LaneOffset.createParallel(finalOffset, a=-lane_offset)
                    

            extendedLanes.add_lanesection(midSecWithTurns)
            extendedLanes.add_lanesection(finalSection)

            self.addLaneOffsets(extendedLanes, turnLaneOffset, finalLaneOffset)

        

        return extendedLanes

            
    
    def getStandardLanesWithInternalTurns(self, n_lanes, lane_offset, laneSides=LaneSides.BOTH,
                            roadLength=None,
                            isLeftTurnLane=False,
                            isRightTurnLane=False,
                            isLeftMergeLane=False,
                            isRightMergeLane=False,
                            numberOfLeftTurnLanesOnRight=0,
                            numberOfRightTurnLanesOnLeft=0,
                            mergeLaneOnTheOppositeSideForInternalTurn=True):

        """Will create numberOfRightTurnLanesOnLeft right turn lanes on the left side of the center line. Equal number of mergelanes will be created on the right side of the center lane, too.
        Will create numberOfLeftTurnLanesOnRight left turn lanes on the right side of the center line. Equal number of mergelanes will be created on the left side of the center lane, too
        Args:
            n_lanes ([type]): [description]
            lane_offset ([type]): [description]
            laneSides ([type], optional): [description]. Defaults to LaneSides.BOTH.
            roadLength ([type], optional): [description]. Defaults to None.
            isLeftTurnLane (bool, optional): [description]. Defaults to False.
            isRightTurnLane (bool, optional): [description]. Defaults to False.
            isLeftMergeLane (bool, optional): [description]. Defaults to False.
            isRightMergeLane (bool, optional): [description]. Defaults to False.
            numberOfLeftTurnLanesOnRight (int, optional): [description]. Defaults to 1.
            numberOfRightTurnLanesOnLeft (int, optional): [description]. Defaults to 1.
        """

        
        if numberOfLeftTurnLanesOnRight > 0 and numberOfRightTurnLanesOnLeft > 0:
            raise Exception(f"Cannot add internal turn lanes on both sides.")

        self.checkTurnAndMergeConflict(isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane)

        self.checkRoadLengthRequirement(isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane, roadLength)


        turnOffSet, finalOffset, curveLaneLength = self.getOffsetsAndTurnLaneCurveLength(roadLength) 
        
        extendedLanes = self.get3SectionLanes(roadLength, turnOffSet, finalOffset, n_lanes_left=n_lanes, n_lanes_right=n_lanes, lane_offset=lane_offset)

        firstSection = extendedLanes.lanesections[0]
        midSection = extendedLanes.lanesections[1]
        finalSection = extendedLanes.lanesections[-1]

        
        # Add turn lanes section if necessary
        self.createTurnLanesAtTheEdges(isLeftTurnLane, isRightTurnLane, lane_offset, curveLaneLength, midSection, finalSection)
        self.createMergeLanesAtTheEdges(isLeftMergeLane, isRightMergeLane, lane_offset, curveLaneLength, midSection, firstSection)
        

        if numberOfRightTurnLanesOnLeft > 0:
            self.createRightTurnLanesOnLeft(numberOfRightTurnLanesOnLeft, extendedLanes, lane_offset, curveLaneLength, firstSection, midSection, finalSection, mergeLaneOnTheOppositeSideForInternalTurn, turnOffSet, finalOffset)
        
        elif numberOfLeftTurnLanesOnRight > 0:
            self.createLeftTurnLanesOnRight(numberOfLeftTurnLanesOnRight, extendedLanes, lane_offset, curveLaneLength, firstSection, midSection, finalSection, mergeLaneOnTheOppositeSideForInternalTurn, turnOffSet, finalOffset)


        return extendedLanes

    
    
    
    def getLanes(self, n_lanes_left, n_lanes_right, lane_offset = None, singleSide=False,
                roadLength=None,
                numLeftTurnsOnLeft=0,
                numRightTurnsOnRight=0,
                numLeftMergeOnLeft=0,
                numRightMergeOnRight=0,
                numberOfLeftTurnLanesOnRight=0,
                numberOfRightTurnLanesOnLeft=0,
                mergeLaneOnTheOppositeSideForInternalTurn=True):
        
        """Always returns 3 lane sections if there is a turn or merge.
        """
        

        if lane_offset is None:
            lane_offset = self.defaultLaneWidth

        if (numLeftTurnsOnLeft == 0 and numRightTurnsOnRight == 0
            and numLeftMergeOnLeft == 0 and numRightMergeOnRight == 0
            and numberOfLeftTurnLanesOnRight == 0  and numberOfRightTurnLanesOnLeft == 0):
            return self.getStandardLanesWithDifferentLeftAndRight(n_lanes_left, n_lanes_right, lane_offset, singleSide)     

        
        if numberOfLeftTurnLanesOnRight > 0 and numberOfRightTurnLanesOnLeft > 0:
            raise Exception(f"Cannot add internal turn lanes on both sides.")

        if roadLength is None:
            raise Exception("road length require for getLanes")

        # self.checkTurnAndMergeConflict(isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane)

        # self.checkRoadLengthRequirement(isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane, roadLength)


        turnOffSet, finalOffset, curveLaneLength = self.getOffsetsAndTurnLaneCurveLength(roadLength) 
        
        extendedLanes = self.get3SectionLanes(roadLength, turnOffSet, finalOffset, n_lanes_left=n_lanes_left, n_lanes_right=n_lanes_right, lane_offset=lane_offset)

        firstSection = extendedLanes.lanesections[0]
        midSection = extendedLanes.lanesections[1]
        finalSection = extendedLanes.lanesections[-1]

        
        # TODO refactor to input number of turns
        self.createLeftTurnLanesOnLeftEdge(numLeftTurnsOnLeft, lane_offset, curveLaneLength, midSection, finalSection)
        self.createRightTurnLanesOnRightEdge(numRightTurnsOnRight, lane_offset, curveLaneLength, midSection, finalSection)

        self.createLeftMergesOnLeftEdge(numLeftMergeOnLeft, lane_offset, curveLaneLength, midSection, firstSection)
        self.createRightMergesOnRightEdge(numRightMergeOnRight, lane_offset, curveLaneLength, midSection, firstSection)


        if numberOfRightTurnLanesOnLeft > 0:
            self.createRightTurnLanesOnLeft(numberOfRightTurnLanesOnLeft, extendedLanes, lane_offset, curveLaneLength, firstSection, midSection, finalSection, mergeLaneOnTheOppositeSideForInternalTurn, turnOffSet, finalOffset)
        
        elif numberOfLeftTurnLanesOnRight > 0:
            self.createLeftTurnLanesOnRight(numberOfLeftTurnLanesOnRight, extendedLanes, lane_offset, curveLaneLength, firstSection, midSection, finalSection, mergeLaneOnTheOppositeSideForInternalTurn, turnOffSet, finalOffset)


        return extendedLanes



    def createLeftTurnLanesOnRight(self, numberOfLeftTurnLanesOnRight, extendedLanes, lane_offset, curveLaneLength, firstSection, midSection, finalSection, mergeLaneOnTheOppositeSideForInternalTurn, turnOffSet, finalOffset):
        for _ in range(numberOfLeftTurnLanesOnRight):
            # 1. we need to change the center lane offset for mid and final

            lane = self.createLinearTurnLane(TurnTypes.LEFT, lane_offset, curveLaneLength)
            midSection.prependLaneToRightLanes(lane)
            finalSection.prependLaneToRightLanes(pyodrx.standard_lane(lane_offset))

            if mergeLaneOnTheOppositeSideForInternalTurn:
                # 2. add a merge lane to left lanes
                lane = self.createLinearMergeLane(lane_offset, curveLaneLength)
                midSection.prependLaneToLeftLanes(lane)
                firstSection.prependLaneToLeftLanes(pyodrx.standard_lane(lane_offset))


        # now the offsets
        # 1. one for turnOffset
        # 2. one for finalOffset
        # we need to shift center lane up.
        turnLaneOffset = LaneOffset.createLinear(turnOffSet, maxWidth=lane_offset * numberOfLeftTurnLanesOnRight, laneLength=curveLaneLength)
        finalLaneOffset = LaneOffset.createParallel(finalOffset, a=lane_offset * numberOfLeftTurnLanesOnRight)
        self.addLaneOffsets(extendedLanes, turnLaneOffset, finalLaneOffset)

        pass


    def createRightTurnLanesOnLeft(self, numberOfRightTurnLanesOnLeft, extendedLanes, lane_offset, curveLaneLength, firstSection, midSection, finalSection, mergeLaneOnTheOppositeSideForInternalTurn, turnOffSet, finalOffset):
        for _ in range(numberOfRightTurnLanesOnLeft):
            # 1. we need to change the center lane offset for mid and final

            lane = self.createLinearTurnLane(TurnTypes.RIGHT, lane_offset, curveLaneLength)
            midSection.prependLaneToLeftLanes(lane)
            finalSection.prependLaneToLeftLanes(pyodrx.standard_lane(lane_offset))

            if mergeLaneOnTheOppositeSideForInternalTurn:
                # 2. add a merge lane to left lanes
                lane = self.createLinearMergeLane(lane_offset, curveLaneLength)
                midSection.prependLaneToRightLanes(lane)
                firstSection.prependLaneToRightLanes(pyodrx.standard_lane(lane_offset))



        # now the offsets
        # 1. one for turnOffset
        # 2. one for finalOffset
        # we need to shift center lane down.

        turnLaneOffset = LaneOffset.createLinear(turnOffSet, maxWidth=-lane_offset * numberOfRightTurnLanesOnLeft, laneLength=curveLaneLength)
        finalLaneOffset = LaneOffset.createParallel(finalOffset, a=-lane_offset * numberOfRightTurnLanesOnLeft)
        self.addLaneOffsets(extendedLanes, turnLaneOffset, finalLaneOffset)

        pass


    def checkRoadLengthRequirement(self, isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane, roadLength):
        if self.anyTurnOrMerge(isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane):
            if roadLength is None:
                raise Exception("Road length cannot be None for turn lanes")



    def checkTurnAndMergeConflict(self, isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane):
        if (isLeftTurnLane or isRightTurnLane) and (isLeftMergeLane or isRightMergeLane):
            raise Exception("merge lane and turn lanes cannot appear in the same road. Please split the road into two for simpler calculations.")


    def getOffsetsAndTurnLaneCurveLength(self, roadLength):
        turnOffSet = 1
        finalOffset = roadLength - 1 # where the final lanesection resides.
        laneLength = finalOffset - turnOffSet 
        return turnOffSet, finalOffset, laneLength


    def addLaneOffsets(self, extendedLanes, turnLaneOffset, finalLaneOffset):

        if turnLaneOffset is not None:
            extendedLanes.addLaneOffset(turnLaneOffset)
        if finalLaneOffset is not None:
            extendedLanes.addLaneOffset(finalLaneOffset)
        pass


    def createLeftTurnLanesOnLeftEdge(self, numLeftTurnsOnLeft, maxWidth, laneLength, midSection, finalSection):

        for _ in range(numLeftTurnsOnLeft):
            lane = self.createLinearTurnLane(TurnTypes.LEFT, maxWidth, laneLength)
            midSection.add_left_lane(lane)
            finalSection.add_left_lane(pyodrx.standard_lane(maxWidth))
        pass


    def createRightTurnLanesOnRightEdge(self, numRightTurnsOnRight, maxWidth, laneLength, midSection, finalSection):

        for _ in range(numRightTurnsOnRight):
            lane = self.createLinearTurnLane(TurnTypes.RIGHT, maxWidth, laneLength)
            midSection.add_right_lane(lane)
            finalSection.add_right_lane(pyodrx.standard_lane(maxWidth))
        
        pass



    def createTurnLanesAtTheEdges(self, isLeftTurnLane, isRightTurnLane, maxWidth, laneLength, midSection, finalSection):
        """curve to the midSection, and parallel to the final section.

        Args:
            isLeftTurnLane (bool): [description]
            isRightTurnLane (bool): [description]
            maxWidth ([type]): [description]
            laneLength ([type]): [description]
            midSection ([type]): [description]
            finalSection ([type]): [description]
        """
        
        if isLeftTurnLane:
            lane = self.createLinearTurnLane(TurnTypes.LEFT, maxWidth, laneLength)
            midSection.add_left_lane(lane)
            finalSection.add_left_lane(pyodrx.standard_lane(maxWidth))

        if isRightTurnLane:
            lane = self.createLinearTurnLane(TurnTypes.RIGHT, maxWidth, laneLength)
            midSection.add_right_lane(lane)
            finalSection.add_right_lane(pyodrx.standard_lane(maxWidth))
        
        pass


    def createLeftMergesOnLeftEdge(self, numLeftMergeOnLeft, maxWidth, laneLength, midSection, firstSection):

        for _ in range(numLeftMergeOnLeft):
            lane = self.createLinearMergeLane(maxWidth, laneLength)
            midSection.add_left_lane(lane)

            firstSection.add_left_lane(pyodrx.standard_lane(maxWidth))
        pass

    def createRightMergesOnRightEdge(self, numRightMergeOnRight, maxWidth, laneLength, midSection, firstSection):

        for _ in range(numRightMergeOnRight):
            lane = self.createLinearMergeLane(maxWidth, laneLength)
            midSection.add_right_lane(lane)

            firstSection.add_right_lane(pyodrx.standard_lane(maxWidth))
        pass
     

    def createMergeLanesAtTheEdges(self, isLeftMergeLane, isRightMergeLane, maxWidth, laneLength, midSection, firstSection):
        if isLeftMergeLane:
            lane = self.createLinearMergeLane(maxWidth, laneLength)
            midSection.add_left_lane(lane)

            firstSection.add_left_lane(pyodrx.standard_lane(maxWidth))

        if isRightMergeLane:
            lane = self.createLinearMergeLane(maxWidth, laneLength)
            midSection.add_right_lane(lane)

            firstSection.add_right_lane(pyodrx.standard_lane(maxWidth))
        pass
    


    def getStandardLaneSection(self, soffset,  
                                n_lanes_left, n_lanes_right,
                                lane_offset,
                                singleSide=False
                                ):

        lsec = extensions.ExtendedLaneSection(soffset, pyodrx.standard_lane(), singleSide=singleSide)

        for _ in range(n_lanes_left):
            lsec.add_left_lane(pyodrx.standard_lane(lane_offset))

        for _ in range(n_lanes_right):
            lsec.add_right_lane(pyodrx.standard_lane(lane_offset))


        return lsec

    
    def get3SectionLanes(self, roadLength, turnOffSet, finalOffset, n_lanes_left=1, n_lanes_right=1, lane_offset=3):
        firstSec = self.getStandardLaneSection(0, n_lanes_left, n_lanes_right, lane_offset=lane_offset)
        midSection = self.getStandardLaneSection(turnOffSet, n_lanes_left, n_lanes_right, lane_offset=lane_offset)
        finalSection = self.getStandardLaneSection(finalOffset, n_lanes_left, n_lanes_right, lane_offset=lane_offset)
        extendedLanes = extensions.ExtendedLanes()
        extendedLanes.add_lanesection(firstSec)
        extendedLanes.add_lanesection(midSection)
        extendedLanes.add_lanesection(finalSection)

        return extendedLanes

    
    ### Section : Turn Lanes

    def createLinearTurnLane(self, turnType, maxWidth, laneLength, soffset=0, laneOffset = 0):

        if laneLength is None:
            raise Exception("Lane length cannot be None for turn lanes")

        if maxWidth is None:
            raise Exception("maxWidth cannot be None for turn lanes")

        a = laneOffset
        b = (maxWidth / laneLength)
        # c = 0
        # c = .1 * (maxWidth / laneLength)

        lane = ExtendedLane(soffset=soffset, a=a, b=b, turnType=turnType)
        return lane


    def addLeftLane(self, road, laneWidth = 3, soffset=0, countryCode=extensions.CountryCodes.US):
        if countryCode == extensions.CountryCodes.US:
            return self.addLefLaneUS(road, laneWidth, soffset=soffset)

        raise NotImplementedError("Only us turns are implemented")


    def addLeftTurnLane(self, road, maxWidth, laneLength = None, countryCode=extensions.CountryCodes.US):
        """Assumes that the last lane section is longer than laneLength
        """

        if countryCode == extensions.CountryCodes.US:
            return self.addLeftTurnLaneUS(road, maxWidth, laneLength)

        raise NotImplementedError("Only us turns are implemented")

    

    def addLefLaneUS(self, road, laneWidth = 3, soffset=0):
        """Assumes that the last lane section is longer than laneLength
        """

        laneSections = road.getLaneSections()

        for laneSection in laneSections:
            lane = pyodrx.Lane(soffset=soffset, a=laneWidth)
            laneSection.add_left_lane(lane)

        pass


    def addLeftTurnLaneUS(self, road, maxWidth, laneLength = None):
        """Assumes that the last lane section is longer than laneLength
        """

        soffset = 0
        if laneLength is not None:
            soffset = road.length() - laneLength
        else:
            laneLength = road.length()

        lane = self.createLinearTurnLane(TurnTypes.LEFT, maxWidth, laneLength, soffset)

        # 2. add lane
        laneSection = road.getLastLaneSection()
        laneSection.add_left_lane(lane)

        raise NotImplementedError("addLeftTurnLaneForUS not implemented")


    def addRightLane(self, road, laneWidth = 3, soffset=0, countryCode=extensions.CountryCodes.US):
        if countryCode == extensions.CountryCodes.US:
            return self.addRightLaneUS(road, laneWidth, soffset=soffset)

        raise NotImplementedError("Only us turns are implemented")



    def addRightTurnLane(self, road, maxWidth, laneLength = None, countryCode=extensions.CountryCodes.US):
        """Assumes that the last lane section is longer than laneLength
        """

        if countryCode == extensions.CountryCodes.US:
            return self.addRightTurnLaneUS(road, maxWidth, laneLength)

        raise NotImplementedError("Only us turns are implemented")


    def addRightTurnLaneUS(self, road, maxWidth, laneLength = None):

        """Assumes that the last lane section is longer than laneLength
        Will not work for 3 lane section plan
        """

        # 1. define lane equation params
        soffset = 0
        if laneLength is not None:
            soffset = road.length() - laneLength
        else:
            laneLength = road.length()

        lane = self.createLinearTurnLane(TurnTypes.RIGHT, maxWidth, laneLength, soffset)

        # 2. add lane
        laneSection = road.getLastLaneSection()
        laneSection.add_right_lane(lane)

        pass


    def addRightLaneUS(self, road, laneWidth = 3, soffset=0):
        """Assumes that the last lane section is longer than laneLength
        """

        laneSections = road.getLaneSections()

        for laneSection in laneSections:
            lane = pyodrx.Lane(soffset=soffset, a=laneWidth)
            laneSection.add_right_lane(lane)

        pass


    ### Section: Merge Lanes

    def createLinearMergeLane(self, maxWidth, laneLength, soffset=0):


        if laneLength is None:
            raise Exception("Lane length cannot be None for turn lanes")

        if maxWidth is None:
            raise Exception("maxWidth cannot be None for turn lanes")

        a = maxWidth
        b = -(maxWidth / laneLength)
        # c = 0
        # c = .1 * (maxWidth / laneLength)

        lane = pyodrx.Lane(soffset=soffset, a=a, b=b)
        return lane

    

    ### Section: Connecting roads

    def createLanesForConnectionRoad(self, connectionRoad: ExtendedRoad, 
                                    predRoad: ExtendedRoad, 
                                    sucRoad: ExtendedRoad, 
                                    strategy = LaneConfigurationStrategies.MERGE_EDGE, 
                                    countryCode=extensions.CountryCodes.US):
        """Assumes start of connection road is connected to predRoad and end to sucRoad and connection road's lanes are not connected to either of the roads.

        Args:
            connectionRoad (ExtendedRoad): 
            predRoad (ExtendedRoad): Extended predecessor road of connectionRoad. That means connection road's start is connected to predRoad
            sucRoad (ExtendedRoad): Extended successor road of connectionRoad. That means connection road's end is connected to sucRoad
            strategy ([type], optional): [description]. Defaults to LaneConfigurationStrategies.MERGE_EDGE.
        """


        try:
            cp1, cp1Con = RoadLinker.getContactPoints(predRoad, connectionRoad)
            cp2, cp2Con = RoadLinker.getContactPoints(sucRoad, connectionRoad)

            laneSection1 = predRoad.getLaneSectionByCP(cp1)
            laneSection2 = sucRoad.getLaneSectionByCP(cp2)

            connectionRoad.clearLanes()

            leftConnections, rightConnections = LaneConfiguration.getLaneLinks(laneSection1, laneSection2, (cp1 == cp2), strategy)

            # now we need to workout the number of straight lanes, merge lanes, and turn lanes on each side.


            # switch lane sides if cp1 and cp1Con are the same, because the lane orientation is reversed

            if cp1 == cp1Con:
                leftNumStandard, leftNumMerge, leftNumTurn = LaneConfiguration.getNumberDifferentLanes(rightConnections)
                rightNumStandard, rightNumMerge, rightNumTurn = LaneConfiguration.getNumberDifferentLanes(leftConnections)
            else:
                leftNumStandard, leftNumMerge, leftNumTurn = LaneConfiguration.getNumberDifferentLanes(leftConnections)
                rightNumStandard, rightNumMerge, rightNumTurn = LaneConfiguration.getNumberDifferentLanes(rightConnections)


            connectionRoad.lanes = self.getLanes(n_lanes_left=leftNumStandard, n_lanes_right=rightNumStandard,
                                 roadLength=connectionRoad.length(),
                                 numLeftTurnsOnLeft=leftNumTurn, numLeftMergeOnLeft=leftNumMerge,
                                 numRightTurnsOnRight= rightNumTurn, numRightMergeOnRight=rightNumMerge)





        
        except Exception as e:
            raise e


    


    