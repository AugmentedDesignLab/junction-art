import pyodrx
import junctions
import extensions
import math
from junctions.LaneSides import LaneSides
from extensions.LaneOffset import LaneOffset


class LaneBuilder:


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
                            lane_offset
                            ):
        """[summary]

        Args:
            n_lanes_left ([type]): [description]
            n_lanes_right ([type]): [description]
            lane_offset ([type]): [description]

        Returns:
            ExtendedLanes : An extended lanes object with 3 lane sections.
        """
                            

        firstSec = self.getStandardLaneSection(0, n_lanes_left, n_lanes_right, lane_offset)
        laneSections = extensions.ExtendedLanes()
        laneSections.add_lanesection(firstSec)
        return laneSections


    def getStandardTurnsOnSingleSide(self, n_lanes, lane_offset, laneSide=LaneSides.RIGHT,
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
            laneSides ([type], optional): where to put lanes wrt center lane. Defaults to LaneSides.RIGHT.

        Returns:
            [type]: Road with one lane section if there is no merge or turn lanes. 3 sections otherwise. 
            In case of turns, the first section will have no turn lanes. In case of merges, the last section will have no merge lanes.
            One side will have no lanes.
        """

        if laneSide == LaneSides.BOTH:
            raise Exception(f"Lanes side can be left or right only.")

        self.checkTurnAndMergeConflict(isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane)

        self.isRoadLengthRequired(isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane, roadLength)

        turnOffSet, finalOffset, curveLaneLength = self.getOffsetsAndTurnLaneCurveLength(roadLength) 

        
        n_lanes_left = 0
        n_lanes_right = 0

        if laneSide == LaneSides.RIGHT:
            n_lanes_right = n_lanes
        else:
            n_lanes_left = n_lanes

        firstSec = self.getStandardLaneSection(0, n_lanes_left, n_lanes_right, lane_offset=lane_offset, singleSide=True)
        midSecWithTurns = self.getStandardLaneSection(turnOffSet, n_lanes_left, n_lanes_right, lane_offset=lane_offset, singleSide=True)
        finalSection = self.getStandardLaneSection(finalOffset, n_lanes_left, n_lanes_right, lane_offset=lane_offset, singleSide=True)

        extendedLanes = extensions.ExtendedLanes()
        extendedLanes.add_lanesection(firstSec)
        

        # 1 add the turn Section
        # 2 final section should have no turns.

        turnLaneOffset = None
        finalLaneOffset = None

        if laneSide == LaneSides.RIGHT:
            if isLeftTurnLane:
                # we need to change the center lane offset for mid and final

                lane = self.createLinearTurnLane(lane_offset, curveLaneLength)
                midSecWithTurns.prependLaneToRightLanes(lane)
                finalSection.prependLaneToRightLanes(pyodrx.standard_lane(lane_offset))

                # now the offsets
                # 1. one for turnOffset
                # 2. one for finalOffset
                turnLaneOffset = LaneOffset.createLinear(turnOffSet, maxWidth=lane_offset, laneLength=curveLaneLength)
                finalLaneOffset = LaneOffset.createParallel(finalOffset, a=lane_offset)
            if isRightTurnLane:
                lane = self.createLinearTurnLane(lane_offset, curveLaneLength)
                midSecWithTurns.add_right_lane(lane)
                finalSection.add_right_lane(pyodrx.standard_lane(lane_offset))
        
        if laneSide == LaneSides.LEFT:
            if isLeftTurnLane:
                lane = self.createLinearTurnLane(lane_offset, curveLaneLength)
                midSecWithTurns.add_left_lane(lane)
                finalSection.add_left_lane(pyodrx.standard_lane(lane_offset))

            if isRightTurnLane:
                # we need to change the center lane offset for mid and final

                lane = self.createLinearTurnLane(lane_offset, curveLaneLength)
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

        self.isRoadLengthRequired(isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane, roadLength)


        turnOffSet, finalOffset, curveLaneLength = self.getOffsetsAndTurnLaneCurveLength(roadLength) 
        
        extendedLanes = self.get3SectionLanes(roadLength, turnOffSet, finalOffset, n_lanes=n_lanes, lane_offset=lane_offset, laneSides=laneSides)

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

    def createLeftTurnLanesOnRight(self, numberOfLeftTurnLanesOnRight, extendedLanes, lane_offset, curveLaneLength, firstSection, midSection, finalSection, mergeLaneOnTheOppositeSideForInternalTurn, turnOffSet, finalOffset):
        for _ in range(numberOfLeftTurnLanesOnRight):
            # 1. we need to change the center lane offset for mid and final

            lane = self.createLinearTurnLane(lane_offset, curveLaneLength)
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

            lane = self.createLinearTurnLane(lane_offset, curveLaneLength)
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


    def isRoadLengthRequired(self, isLeftTurnLane, isRightTurnLane, isLeftMergeLane, isRightMergeLane, roadLength):
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
            lane = self.createLinearTurnLane(maxWidth, laneLength)
            midSection.add_left_lane(lane)
            finalSection.add_left_lane(pyodrx.standard_lane(maxWidth))

        if isRightTurnLane:
            lane = self.createLinearTurnLane(maxWidth, laneLength)
            midSection.add_right_lane(lane)
            finalSection.add_right_lane(pyodrx.standard_lane(maxWidth))
        
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

    
    def get3SectionLanes(self, roadLength, turnOffSet, finalOffset, n_lanes=1, lane_offset=3, laneSides=LaneSides.BOTH):
        firstSec = self.getStandardLaneSection(0, n_lanes, n_lanes, lane_offset=lane_offset)
        midSection = self.getStandardLaneSection(turnOffSet, n_lanes, n_lanes, lane_offset=lane_offset)
        finalSection = self.getStandardLaneSection(finalOffset, n_lanes, n_lanes, lane_offset=lane_offset)
        extendedLanes = extensions.ExtendedLanes()
        extendedLanes.add_lanesection(firstSec)
        extendedLanes.add_lanesection(midSection)
        extendedLanes.add_lanesection(finalSection)

        return extendedLanes

    
    ### Section : Turn Lanes

    def createLinearTurnLane(self, maxWidth, laneLength, soffset=0):

        if laneLength is None:
            raise Exception("Lane length cannot be None for turn lanes")

        if maxWidth is None:
            raise Exception("maxWidth cannot be None for turn lanes")

        a = 0
        b = (maxWidth / laneLength)
        # c = 0
        # c = .1 * (maxWidth / laneLength)

        lane = pyodrx.Lane(soffset=soffset, a=a, b=b)
        return lane



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

        lane = self.createLinearTurnLane(maxWidth, laneLength, soffset)

        # 2. add lane
        laneSection = road.getEndLaneSection()
        laneSection.add_left_lane(lane)

        raise NotImplementedError("addLeftTurnLaneForUS not implemented")


    def addRightTurnLaneUS(self, road, maxWidth, laneLength = None):

        """Assumes that the last lane section is longer than laneLength
        """

        # 1. define lane equation params
        soffset = 0
        if laneLength is not None:
            soffset = road.length() - laneLength
        else:
            laneLength = road.length()

        lane = self.createLinearTurnLane(maxWidth, laneLength, soffset)

        # 2. add lane
        laneSection = road.getEndLaneSection()
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

    


    