import pyodrx
import junctions
import extensions
import math
from junctions.LaneSides import LaneSides
from extensions.LaneOffset import LaneOffset


class LaneBuilder:


    def getStandardLanes(self, n_lanes, lane_offset, laneSides=LaneSides.BOTH,
                            roadLength = None,
                            leftTurnLane=False,
                            rightTurnLane=False,
                            leftMergeLane=False,
                            rightMergeLane=False):
        """[summary] Don't allow both merge lanes and turn lanes in a road. Better split to two roads
        TODO allow merge and turn in opposite sides of a road

        Args:
            n_lanes ([type]): [description]
            lane_offset ([type]): width
            laneSides ([type], optional): where to put lanes wrt center lane. Defaults to LaneSides.BOTH.

        Returns:
            [type]: Road with one lane section if there is no merge or turn lanes. 3 sections otherwise. In case of turns, the first section will have no turn lanes. In case of merges, the last section will have no merge lanes.
        """

        if (leftTurnLane or rightTurnLane) and (leftMergeLane or rightMergeLane):
            raise Exception("merge lane and turn lanes cannot appear in the same road. Please split the road into two for simpler calculations.")


        firstSec = self.getStandardLaneSection(0, n_lanes, laneSides, lane_offset)
        laneSections = extensions.ExtendedLanes()
        laneSections.add_lanesection(firstSec)
        
        # Add turn lanes section if necessary
        if leftTurnLane or rightTurnLane:
            if roadLength is None:
                raise Exception("Road length cannot be None for turn lanes")
            
            turnOffSet = 1
            finalOffset = roadLength - 1 # where the final lanesection resides.
            laneLength = finalOffset - turnOffSet 

            # 1 add the turn Section
            # 2 final section should have no turns.

            midSecWithTurns = self.getStandardLaneSection(turnOffSet, n_lanes, laneSides, lane_offset)
            finalSection = self.getStandardLaneSection(finalOffset, n_lanes, laneSides, lane_offset)
            if leftTurnLane:
                lane = self.createLinearTurnLane(lane_offset, laneLength)
                midSecWithTurns.add_left_lane(lane)

                finalSection.add_left_lane(pyodrx.standard_lane(lane_offset))

            if rightTurnLane:
                lane = self.createLinearTurnLane(lane_offset, laneLength)
                midSecWithTurns.add_right_lane(lane)

                finalSection.add_right_lane(pyodrx.standard_lane(lane_offset))

            laneSections.add_lanesection(midSecWithTurns)
            laneSections.add_lanesection(finalSection)

        if leftMergeLane or rightMergeLane:
            if roadLength is None:
                raise Exception("Road length cannot be None for turn lanes")
            
            turnOffSet = 1
            finalOffset = roadLength - 1 # where the final lanesection resides.
            laneLength = finalOffset - turnOffSet 

            # 1 add the MERGE Section
            # 2 final section should have no turns.
            # 3 first section will have merge lanes

            midSecWithMerges = self.getStandardLaneSection(turnOffSet, n_lanes, laneSides, lane_offset)
            finalSection = self.getStandardLaneSection(finalOffset, n_lanes, laneSides, lane_offset)
            if leftMergeLane:
                lane = self.createLinearMergeLane(lane_offset, laneLength)
                midSecWithMerges.add_left_lane(lane)

                firstSec.add_left_lane(pyodrx.standard_lane(lane_offset))

            if rightMergeLane:
                lane = self.createLinearMergeLane(lane_offset, laneLength)
                midSecWithMerges.add_right_lane(lane)

                firstSec.add_right_lane(pyodrx.standard_lane(lane_offset))

            laneSections.add_lanesection(midSecWithMerges)
            laneSections.add_lanesection(finalSection)


        return laneSections



    def getStandardSingleSide(self, n_lanes, lane_offset, laneSide=LaneSides.RIGHT,
                            roadLength = None,
                            leftTurnLane=False,
                            rightTurnLane=False,
                            leftMergeLane=False,
                            rightMergeLane=False):
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

        if (leftTurnLane or rightTurnLane) and (leftMergeLane or rightMergeLane):
            raise Exception("merge lane and turn lanes cannot appear in the same road. Please split the road into two for simpler calculations.")

        

        firstSec = self.getStandardLaneSection(0, n_lanes, laneSides=laneSide, lane_offset=lane_offset)
        extendedLanes = extensions.ExtendedLanes()
        extendedLanes.add_lanesection(firstSec)
        
        # Add turn lanes section if necessary
        if leftTurnLane or rightTurnLane:
            if roadLength is None:
                raise Exception("Road length cannot be None for turn lanes")
            
            turnOffSet = 1
            finalOffset = roadLength - 1 # where the final lanesection resides.
            laneLength = finalOffset - turnOffSet 

            # 1 add the turn Section
            # 2 final section should have no turns.

            midSecWithTurns = self.getStandardLaneSection(turnOffSet, n_lanes, laneSides=laneSide, lane_offset=lane_offset)
            finalSection = self.getStandardLaneSection(finalOffset, n_lanes, laneSides=laneSide, lane_offset=lane_offset)
            turnLaneOffset = None
            finalLaneOffset = None

            if laneSide == LaneSides.RIGHT:
                if leftTurnLane:
                    # we need to change the center lane offset for mid and final

                    lane = self.createLinearTurnLane(lane_offset, laneLength)
                    midSecWithTurns.addLeftLaneToRightLanes(lane)
                    finalSection.add_left_lane(pyodrx.standard_lane(lane_offset))

                    # now the offsets
                    # 1. one for turnOffset
                    # 2. one for finalOffset
                    turnLaneOffset = LaneOffset.createLinear(turnOffSet, maxWidth=lane_offset, laneLength=laneLength)
                    finalLaneOffset = LaneOffset.createParallel(finalOffset, a=lane_offset)

            extendedLanes.add_lanesection(midSecWithTurns)
            extendedLanes.add_lanesection(finalSection)

            if turnLaneOffset is not None:
                extendedLanes.addLaneOffset(turnLaneOffset)
            if finalLaneOffset is not None:
                extendedLanes.addLaneOffset(finalLaneOffset)



        return extendedLanes


    def getStandardLaneSection(self, soffset,  n_lanes, laneSides, lane_offset):

        lsec = extensions.ExtendedLaneSection(soffset, pyodrx.standard_lane())
        for _ in range(1, n_lanes + 1, 1):
            if laneSides == LaneSides.BOTH:
                lsec.add_right_lane(pyodrx.standard_lane(lane_offset))
                lsec.add_left_lane(pyodrx.standard_lane(lane_offset))
            elif laneSides == LaneSides.LEFT:
                lsec.add_left_lane(pyodrx.standard_lane(lane_offset))
            else:
                lsec.add_right_lane(pyodrx.standard_lane(lane_offset))

        return lsec

    

    
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

    


    