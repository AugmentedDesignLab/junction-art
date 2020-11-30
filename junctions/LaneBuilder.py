import pyodrx
import junctions
import extensions
import math
from junctions.LaneSides import LaneSides


class LaneBuilder:


    def getStandardLanes(self, n_lanes, lane_offset, laneSides=LaneSides.BOTH,
                            roadLength = None,
                            leftTurnLane=False,
                            rightTurnLane=False):
        """[summary]

        Args:
            n_lanes ([type]): [description]
            lane_offset ([type]): width
            laneSides ([type], optional): where to put lanes wrt center lane. Defaults to LaneSides.BOTH.

        Returns:
            [type]: [description]
        """
        lsec = self.getStandardLaneSection(0, n_lanes, laneSides, lane_offset)
        laneSections = extensions.LaneSections()
        laneSections.add_lanesection(lsec)
        
        # Add turn lanes section if necessary
        if leftTurnLane or rightTurnLane:
            if roadLength is None:
                raise Exception("Road length cannot be None for turn lanes")
            
            turnOffSet = 1
            finalOffset = roadLength - 1 # where the final lanesection resides.
            laneLength = finalOffset - turnOffSet 

            # 1 add the turns

            lsecWithTurns = self.getStandardLaneSection(turnOffSet, n_lanes, laneSides, lane_offset)
            lsecFinal = self.getStandardLaneSection(finalOffset, n_lanes, laneSides, lane_offset)
            if leftTurnLane:
                lane = self.getTurnLane(lane_offset, laneLength)
                lsecWithTurns.add_left_lane(lane)

                lsecFinal.add_left_lane(pyodrx.standard_lane(lane_offset))

            if rightTurnLane:
                lane = self.getTurnLane(lane_offset, laneLength)
                lsecWithTurns.add_right_lane(lane)

                lsecFinal.add_right_lane(pyodrx.standard_lane(lane_offset))

            laneSections.add_lanesection(lsecWithTurns)
            laneSections.add_lanesection(lsecFinal)

            # 2 final section should have no turns.


        return laneSections


    def getStandardLaneSection(self, soffset,  n_lanes, laneSides, lane_offset):

        lsec = pyodrx.LaneSection(soffset, pyodrx.standard_lane())
        for _ in range(1, n_lanes + 1, 1):
            if laneSides == LaneSides.BOTH:
                lsec.add_right_lane(pyodrx.standard_lane(lane_offset))
                lsec.add_left_lane(pyodrx.standard_lane(lane_offset))
            elif laneSides == LaneSides.LEFT:
                lsec.add_left_lane(pyodrx.standard_lane(lane_offset))
            else:
                lsec.add_right_lane(pyodrx.standard_lane(lane_offset))

        return lsec


    
    
    def getTurnLane(self, maxWidth, laneLength):

        if laneLength is None:
            raise Exception("Lane length cannot be None for turn lanes")

        if maxWidth is None:
            raise Exception("maxWidth cannot be None for turn lanes")

        soffset = 0

        a = 0
        b = (maxWidth / laneLength)
        # c = 0
        # c = .1 * (maxWidth / laneLength)

        lane = pyodrx.Lane(soffset=soffset, a=a, b=b)
        return lane



    def addLeftTurnLane(self, road, countryCode=extensions.CountryCodes.US):
        """Assumes that the last lane section is longer than laneLength
        """

        if countryCode == extensions.CountryCodes.US:
            return self.addLeftTurnLaneForUS(road)

        raise NotImplementedError("Only us turns are implemented")

    
    def addLeftTurnLaneForUS(self, road):
        """Assumes that the last lane section is longer than laneLength
        """

        raise NotImplementedError("addLeftTurnLaneForUS not implemented")


    def addRightTurnLaneUS(self, road, maxWidth, laneLength = None):

        """Assumes that the last lane section is longer than laneLength
        """

        # 1. define lane equation params
        soffset = 0
        if laneLength is not None:
            soffset = road.length() - laneLength

        a = 0
        b = (maxWidth / laneLength)
        # c = 0
        # c = .1 * (maxWidth / laneLength)

        lane = pyodrx.Lane(soffset=soffset, a=a, b=b)


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

