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
            [type]: Road with one lane section if there is no merge or turn lanes. 3 sections otherwise. In case of turns, the first section will have no turn lanes. In case of merges, the last section will have no merge lanes.
        """

        if (isLeftTurnLane or isRightTurnLane) and (isLeftMergeLane or isRightMergeLane):
            raise Exception("merge lane and turn lanes cannot appear in the same road. Please split the road into two for simpler calculations.")

        if laneSides != LaneSides.BOTH:
            return self.getStandardSingleSide(n_lanes, lane_offset, laneSides,
                                            roadLength=roadLength, 
                                            isLeftTurnLane=isLeftTurnLane, isRightTurnLane=isRightTurnLane,
                                            isLeftMergeLane=isLeftMergeLane, isRightMergeLane=isRightMergeLane
                                        )

        firstSec = self.getStandardLaneSection(0, n_lanes, n_lanes, lane_offset)
        laneSections = extensions.ExtendedLanes()
        laneSections.add_lanesection(firstSec)
        
        # Add turn lanes section if necessary
        if isLeftTurnLane or isRightTurnLane:
            if roadLength is None:
                raise Exception("Road length cannot be None for turn lanes")
            
            turnOffSet = 1
            finalOffset = roadLength - 1 # where the final lanesection resides.
            laneLength = finalOffset - turnOffSet 

            # 1 add the turn Section
            # 2 final section should have no turns.

            midSecWithTurns = self.getStandardLaneSection(turnOffSet, n_lanes, n_lanes, lane_offset)
            finalSection = self.getStandardLaneSection(finalOffset, n_lanes, n_lanes, lane_offset)
            if isLeftTurnLane:
                lane = self.createLinearTurnLane(lane_offset, laneLength)
                midSecWithTurns.add_left_lane(lane)

                finalSection.add_left_lane(pyodrx.standard_lane(lane_offset))

            if isRightTurnLane:
                lane = self.createLinearTurnLane(lane_offset, laneLength)
                midSecWithTurns.add_right_lane(lane)

                finalSection.add_right_lane(pyodrx.standard_lane(lane_offset))

            laneSections.add_lanesection(midSecWithTurns)
            laneSections.add_lanesection(finalSection)

        if isLeftMergeLane or isRightMergeLane:
            if roadLength is None:
                raise Exception("Road length cannot be None for turn lanes")
            
            turnOffSet = 1
            finalOffset = roadLength - 1 # where the final lanesection resides.
            laneLength = finalOffset - turnOffSet 

            # 1 add the MERGE Section
            # 2 final section should have no turns.
            # 3 first section will have merge lanes

            midSecWithMerges = self.getStandardLaneSection(turnOffSet, n_lanes, n_lanes, lane_offset)
            finalSection = self.getStandardLaneSection(finalOffset, n_lanes, n_lanes, lane_offset)
            if isLeftMergeLane:
                lane = self.createLinearMergeLane(lane_offset, laneLength)
                midSecWithMerges.add_left_lane(lane)

                firstSec.add_left_lane(pyodrx.standard_lane(lane_offset))

            if isRightMergeLane:
                lane = self.createLinearMergeLane(lane_offset, laneLength)
                midSecWithMerges.add_right_lane(lane)

                firstSec.add_right_lane(pyodrx.standard_lane(lane_offset))

            laneSections.add_lanesection(midSecWithMerges)
            laneSections.add_lanesection(finalSection)


        return laneSections


    def getStandardLanesWithDifferentLeftAndRight(self,
                            n_lanes_left, n_lanes_right,
                            lane_offset
                            ):
                            


        firstSec = self.getStandardLaneSection(0, n_lanes_left, n_lanes_right, lane_offset)
        laneSections = extensions.ExtendedLanes()
        laneSections.add_lanesection(firstSec)
        

        return laneSections


    def getStandardSingleSide(self, n_lanes, lane_offset, laneSide=LaneSides.RIGHT,
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
            [type]: Road with one lane section if there is no merge or turn lanes. 3 sections otherwise. In case of turns, the first section will have no turn lanes. In case of merges, the last section will have no merge lanes.
        """

        if laneSide == LaneSides.BOTH:
            raise Exception(f"Lanes side can be left or right only.")

        if (isLeftTurnLane or isRightTurnLane) and (isLeftMergeLane or isRightMergeLane):
            raise Exception("merge lane and turn lanes cannot appear in the same road. Please split the road into two for simpler calculations.")

        

        firstSec = self.getStandardLaneSection(0, n_lanes, n_lanes, lane_offset=lane_offset)
        extendedLanes = extensions.ExtendedLanes()
        extendedLanes.add_lanesection(firstSec)
        
        # Add turn lanes section if necessary
        if isLeftTurnLane or isRightTurnLane:
            if roadLength is None:
                raise Exception("Road length cannot be None for turn lanes")
            
            turnOffSet = 1
            finalOffset = roadLength - 1 # where the final lanesection resides.
            laneLength = finalOffset - turnOffSet 

            # 1 add the turn Section
            # 2 final section should have no turns.

            midSecWithTurns = self.getStandardLaneSection(turnOffSet, n_lanes, n_lanes, lane_offset=lane_offset)
            finalSection = self.getStandardLaneSection(finalOffset, n_lanes, n_lanes, lane_offset=lane_offset)
            turnLaneOffset = None
            finalLaneOffset = None

            if laneSide == LaneSides.RIGHT:
                if isLeftTurnLane:
                    # we need to change the center lane offset for mid and final

                    lane = self.createLinearTurnLane(lane_offset, laneLength)
                    midSecWithTurns.addLeftLaneToRightLanes(lane)
                    finalSection.addLeftLaneToRightLanes(pyodrx.standard_lane(lane_offset))

                    # now the offsets
                    # 1. one for turnOffset
                    # 2. one for finalOffset
                    turnLaneOffset = LaneOffset.createLinear(turnOffSet, maxWidth=lane_offset, laneLength=laneLength)
                    finalLaneOffset = LaneOffset.createParallel(finalOffset, a=lane_offset)
                if isRightTurnLane:
                    lane = self.createLinearTurnLane(lane_offset, laneLength)
                    midSecWithTurns.add_right_lane(lane)
                    finalSection.add_right_lane(pyodrx.standard_lane(lane_offset))
            
            if laneSide == LaneSides.LEFT:
                if isLeftTurnLane:
                    lane = self.createLinearTurnLane(lane_offset, laneLength)
                    midSecWithTurns.add_left_lane(lane)
                    finalSection.add_left_lane(pyodrx.standard_lane(lane_offset))

                if isRightTurnLane:
                    # we need to change the center lane offset for mid and final

                    lane = self.createLinearTurnLane(lane_offset, laneLength)
                    midSecWithTurns.addRightLaneToLeftLanes(lane)
                    finalSection.addRightLaneToLeftLanes(pyodrx.standard_lane(lane_offset))

                    # now the offsets
                    # 1. one for turnOffset
                    # 2. one for finalOffset
                    turnLaneOffset = LaneOffset.createLinear(turnOffSet, maxWidth=-lane_offset, laneLength=laneLength)
                    finalLaneOffset = LaneOffset.createParallel(finalOffset, a=-lane_offset)
                    

            extendedLanes.add_lanesection(midSecWithTurns)
            extendedLanes.add_lanesection(finalSection)

            if turnLaneOffset is not None:
                extendedLanes.addLaneOffset(turnLaneOffset)
            if finalLaneOffset is not None:
                extendedLanes.addLaneOffset(finalLaneOffset)



        return extendedLanes

    

    def getStandardLanesWithLeftTurnLanesOnRight(self, n_lanes, lane_offset, laneSides=LaneSides.BOTH,
                            roadLength = None,
                            isLeftTurnLane=False,
                            isRightTurnLane=False,
                            isLeftMergeLane=False,
                            isRightMergeLane=False,
                            numberOfLeftTurnLanesOnRight=1):

        """Will create numberOfLeftTurnLanesOnRight left turn lanes on the right side of the center line. Equal number of mergelanes will be created on the left side of the center lane, too.

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

        Raises:
            Exception: [description]
            Exception: [description]

        Returns:
            [type]: [description]
        """
        

        if (isLeftTurnLane or isRightTurnLane) and (isLeftMergeLane or isRightMergeLane):
            raise Exception("merge lane and turn lanes cannot appear in the same road. Please split the road into two for simpler calculations.")

        if roadLength is None:
            raise Exception("Road length cannot be None for turn lanes")

        # if numberOfLeftTurnLanesOnRight != 1:
        #     raise Exception("only one internal turn lane implemented")

        turnOffSet = 1
        finalOffset = roadLength - 1 # where the final lanesection resides.
        laneLength = finalOffset - turnOffSet 
        
        extendedLanes = self.get3SectionLanes(roadLength, turnOffSet, finalOffset, n_lanes=n_lanes, lane_offset=lane_offset, laneSides=laneSides)

        firstSection = extendedLanes.lanesections[0]
        midSection = extendedLanes.lanesections[1]
        finalSection = extendedLanes.lanesections[-1]

        
        firstLaneOffset = extendedLanes.laneOffsets[0]
        turnLaneOffset = None
        finalLaneOffset = None


        for _ in range(numberOfLeftTurnLanesOnRight):
            # 1. we need to change the center lane offset for mid and final

            lane = self.createLinearTurnLane(lane_offset, laneLength)
            midSection.addLeftLaneToRightLanes(lane)
            finalSection.addLeftLaneToRightLanes(pyodrx.standard_lane(lane_offset))

            # 2. add a merge lane to left lanes

            lane = self.createLinearMergeLane(lane_offset, laneLength)
            midSection.addRightLaneToLeftLanes(lane)
            firstSection.addRightLaneToLeftLanes(pyodrx.standard_lane(lane_offset))

        
        # Add turn lanes section if necessary
        self.createTurnLanesAtTheEnd(isLeftTurnLane, isRightTurnLane, lane_offset, laneLength, midSection, finalSection)


        # now the offsets
        # 1. one for turnOffset
        # 2. one for finalOffset
        turnLaneOffset = LaneOffset.createLinear(turnOffSet, maxWidth=lane_offset * numberOfLeftTurnLanesOnRight, laneLength=laneLength)
        finalLaneOffset = LaneOffset.createParallel(finalOffset, a=lane_offset * numberOfLeftTurnLanesOnRight)

        if turnLaneOffset is not None:
            extendedLanes.addLaneOffset(turnLaneOffset)
        if finalLaneOffset is not None:
            extendedLanes.addLaneOffset(finalLaneOffset)

        return extendedLanes

    def createTurnLanesAtTheEnd(self, isLeftTurnLane, isRightTurnLane, lane_offset, laneLength, midSection, finalSection):
        if isLeftTurnLane or isRightTurnLane:

            # 1 add the turn Section
            # 2 final section should have no turns.
            if isLeftTurnLane:
                lane = self.createLinearTurnLane(lane_offset, laneLength)
                midSection.add_left_lane(lane)
                finalSection.add_left_lane(pyodrx.standard_lane(lane_offset))

            if isRightTurnLane:
                lane = self.createLinearTurnLane(lane_offset, laneLength)
                midSection.add_right_lane(lane)
                finalSection.add_right_lane(pyodrx.standard_lane(lane_offset))
     


    def getStandardLaneSection(self, soffset,  
                                n_lanes_left, n_lanes_right,
                                lane_offset
                                ):

        lsec = extensions.ExtendedLaneSection(soffset, pyodrx.standard_lane())

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

    


    